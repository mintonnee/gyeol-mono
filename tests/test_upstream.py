import hashlib
import zipfile
from pathlib import Path

import pytest

from gyeol_mono.upstream import (
    ChecksumError,
    ManifestError,
    UpstreamSource,
    fetch_source,
    load_manifest,
)

PROJECT_ROOT = Path(__file__).parents[1]


def test_project_manifest_pins_all_canonical_sources() -> None:
    manifest = load_manifest(PROJECT_ROOT / "sources.toml")

    assert {source.id for source in manifest.sources} == {
        "ibm-plex-mono",
        "maru-buri",
        "ridi-batang",
        "klee-one",
        "ibm-plex-sans-jp",
    }
    klee = manifest.select(("klee-one",))[0]
    assert klee.revision == "8b0532731b63ad8a445ca341d8d7d941079b83ab"
    assert all(len(source.sha256) == 64 for source in manifest.sources)
    ridi = manifest.select(("ridi-batang",))[0]
    assert ridi.role == "hangul-comparison-only"
    assert ridi.archive_format == "file"
    assert ridi.files == ("RIDIBatang.otf",)
    assert manifest.select(("maru-buri",))[0].role == "hangul"


def test_fetch_verifies_and_extracts_only_declared_files(tmp_path: Path) -> None:
    archive = tmp_path / "fixture.zip"
    with zipfile.ZipFile(archive, "w") as fixture:
        fixture.writestr("fonts/Regular.ttf", b"regular")
        fixture.writestr("ignored.txt", b"ignored")
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    source = UpstreamSource(
        id="fixture",
        role="test",
        version="1",
        release_page="https://example.com/release",
        url="https://example.com/fixture.zip",
        archive="fixture.zip",
        sha256=digest,
        files=("fonts/Regular.ttf",),
    )
    output = tmp_path / "upstream"
    archive_dir = output / "archives"
    archive_dir.mkdir(parents=True)
    archive.replace(archive_dir / source.archive)

    result = fetch_source(source, output)

    assert not result.downloaded
    assert result.files[0].read_bytes() == b"regular"
    assert not (output / source.id / "ignored.txt").exists()


def test_fetch_rejects_existing_archive_with_wrong_checksum(tmp_path: Path) -> None:
    source = UpstreamSource(
        id="fixture",
        role="test",
        version="1",
        release_page="https://example.com/release",
        url="https://example.com/fixture.zip",
        archive="fixture.zip",
        sha256="0" * 64,
        files=("font.ttf",),
    )
    archive_dir = tmp_path / "archives"
    archive_dir.mkdir()
    (archive_dir / source.archive).write_bytes(b"wrong")

    with pytest.raises(ChecksumError, match="rerun with --force"):
        fetch_source(source, tmp_path)


def test_manifest_rejects_unsafe_member() -> None:
    with pytest.raises(ManifestError, match="unsafe archive member"):
        UpstreamSource(
            id="fixture",
            role="test",
            version="1",
            release_page="https://example.com/release",
            url="https://example.com/fixture.zip",
            archive="fixture.zip",
            sha256="0" * 64,
            files=("../font.ttf",),
        )


def test_fetch_raw_file_downloads_verifies_and_reuses_cache(tmp_path, monkeypatch) -> None:
    from io import BytesIO

    payload = b"fixture OTF bytes"
    source = UpstreamSource(
        id="raw",
        role="hangul",
        version="1",
        release_page="https://example.com/",
        url="https://example.com/font.otf",
        archive="font-v1.otf",
        sha256=hashlib.sha256(payload).hexdigest(),
        files=("font.otf",),
        archive_format="file",
    )
    requests = []

    def download(request, timeout):
        requests.append(request.full_url)
        return BytesIO(payload)

    monkeypatch.setattr("gyeol_mono.upstream.urlopen", download)
    first = fetch_source(source, tmp_path)
    assert first.downloaded
    assert first.files == (tmp_path / "raw/font.otf",)
    assert first.files[0].read_bytes() == payload
    second = fetch_source(source, tmp_path)
    assert not second.downloaded
    assert len(requests) == 1
    first.archive.write_bytes(b"corrupt")
    with pytest.raises(ChecksumError):
        fetch_source(source, tmp_path)
    assert first.files[0].read_bytes() == payload


@pytest.mark.parametrize(
    "archive_format,files",
    [
        ("tar", ("font.otf",)),
        ("file", ("a.otf", "b.otf")),
        ("file", ("../font.otf",)),
    ],
)
def test_raw_source_rejects_invalid_format_or_members(archive_format, files):
    with pytest.raises(ManifestError):
        UpstreamSource(
            id="raw",
            role="hangul",
            version="1",
            release_page="https://example.com/",
            url="https://example.com/font.otf",
            archive="font.otf",
            sha256="0" * 64,
            files=files,
            archive_format=archive_format,
        )
