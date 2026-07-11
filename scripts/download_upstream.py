"""Download the sources pinned in sources.toml."""

import sys

from gyeol_mono.cli import main

if __name__ == "__main__":
    raise SystemExit(main(["fetch", *sys.argv[1:]]))
