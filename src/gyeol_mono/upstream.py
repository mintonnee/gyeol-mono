"""Pinned upstream source manifest and checksum-verifying downloader."""

import hashlib
import re
import shutil
import tomllib
import zipfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from urllib.request import Request, urlopen

MANIFEST_SCHEMA_VERSION = 1
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")


class ManifestError(ValueError):
    """Raised when the upstream manifest is malformed."""


class ChecksumError(RuntimeError):
    """Raised when an archive does not match its pinned SHA-256."""


@dataclass(frozen=True, slots=True)
class UpstreamSource:
    id: str
    role: str
    version: str
    release_page: str
    url: str
    archive: str
    sha256: str
    files: tuple[str, ...]
    revision: str | None = None
    license_url: str | None = None

    def __post_init__(self) -> None:
        if not self.id or not self.files:
            raise ManifestError("source id and files must not be empty")
        if not SHA256_PATTERN.fullmatch(self.sha256):
            raise ManifestError(f"invalid SHA-256 for {self.id}: {self.sha256}")
        if not self.url.startswith("https://") or not self.release_page.startswith("https://"):
            raise ManifestError(f"source URLs must use HTTPS: {self.id}")
        for member in self.files:
            path = PurePosixPath(member)
            if path.is_absolute() or ".." in path.parts:
                raise ManifestError(f"unsafe archive member for {self.id}: {member}")


@dataclass(frozen=True, slots=True)
class UpstreamManifest:
    sources: tuple[UpstreamSource, ...]

    def select(self, source_ids: tuple[str, ...] = ()) -> tuple[UpstreamSource, ...]:
        if not source_ids:
            return self.sources
        by_id = {source.id: source for source in self.sources}
        unknown = sorted(set(source_ids) - by_id.keys())
        if unknown:
            raise ManifestError(f"unknown source id: {', '.join(unknown)}")
        return tuple(by_id[source_id] for source_id in source_ids)


@dataclass(frozen=True, slots=True)
class FetchResult:
    source_id: str
    archive: Path
    files: tuple[Path, ...]
    downloaded: bool


def load_manifest(path: Path) -> UpstreamManifest:
    with path.open("rb") as manifest_file:
        data = tomllib.load(manifest_file)

    if data.get("schema_version") != MANIFEST_SCHEMA_VERSION:
        raise ManifestError(f"unsupported manifest schema: {data.get('schema_version')}")

    try:
        sources = tuple(
            UpstreamSource(
                id=item["id"],
                role=item["role"],
                version=item["version"],
                release_page=item["release_page"],
                url=item["url"],
                archive=item["archive"],
                sha256=item["sha256"],
                files=tuple(item["files"]),
                revision=item.get("revision"),
                license_url=item.get("license_url"),
            )
            for item in data["source"]
        )
    except (KeyError, TypeError) as error:
        raise ManifestError(f"invalid source entry: {error}") from error

    source_ids = [source.id for source in sources]
    if len(source_ids) != len(set(source_ids)):
        raise ManifestError("source ids must be unique")
    return UpstreamManifest(sources)


def sha256(path: Path) -> str:
    with path.open("rb") as file:
        return hashlib.file_digest(file, "sha256").hexdigest()


def fetch_source(source: UpstreamSource, destination: Path, *, force: bool = False) -> FetchResult:
    archive_dir = destination / "archives"
    archive_dir.mkdir(parents=True, exist_ok=True)
    archive_path = archive_dir / source.archive

    downloaded = False
    if archive_path.exists() and sha256(archive_path) != source.sha256 and not force:
        raise ChecksumError(
            f"existing archive checksum mismatch: {archive_path}; rerun with --force"
        )
    if force or not archive_path.exists():
        _download_verified(source, archive_path)
        downloaded = True

    extracted = _extract_declared_files(source, archive_path, destination / source.id)
    return FetchResult(source.id, archive_path, extracted, downloaded)


def _download_verified(source: UpstreamSource, archive_path: Path) -> None:
    partial_path = archive_path.with_suffix(f"{archive_path.suffix}.part")
    partial_path.unlink(missing_ok=True)
    request = Request(source.url, headers={"User-Agent": "gyeol-mono/0.1"})
    try:
        with urlopen(request, timeout=60) as response, partial_path.open("wb") as output:
            shutil.copyfileobj(response, output)
        actual = sha256(partial_path)
        if actual != source.sha256:
            raise ChecksumError(
                f"download checksum mismatch for {source.id}: "
                f"expected {source.sha256}, got {actual}"
            )
        partial_path.replace(archive_path)
    except Exception:
        partial_path.unlink(missing_ok=True)
        raise


def _extract_declared_files(
    source: UpstreamSource, archive_path: Path, destination: Path
) -> tuple[Path, ...]:
    with zipfile.ZipFile(archive_path) as archive:
        missing = sorted(set(source.files) - set(archive.namelist()))
        if missing:
            raise ManifestError(
                f"archive for {source.id} is missing declared files: {', '.join(missing)}"
            )

        extracted = []
        for member in source.files:
            relative_path = PurePosixPath(member)
            output_path = destination.joinpath(*relative_path.parts)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            partial_path = output_path.with_suffix(f"{output_path.suffix}.part")
            with archive.open(member) as input_file, partial_path.open("wb") as output_file:
                shutil.copyfileobj(input_file, output_file)
            partial_path.replace(output_path)
            extracted.append(output_path)
    return tuple(extracted)
