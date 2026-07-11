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
        "klee-one",
        "ibm-plex-sans-jp",
    }
    klee = manifest.select(("klee-one",))[0]
    assert klee.revision == "8b0532731b63ad8a445ca341d8d7d941079b83ab"
    assert all(len(source.sha256) == 64 for source in manifest.sources)


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
