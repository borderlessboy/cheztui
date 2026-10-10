"""cheztui command line.

    cheztui                     the TUI (on a terminal), else help

Exit codes: 0 ok, 1 some target failed or was refused, 2 usage/config error,
3 chezmoi missing or broken.
"""

from __future__ import annotations

import argparse
import sys

from cheztui import __version__

EXIT_OK, EXIT_FAILED, EXIT_USAGE, EXIT_CHEZMOI = 0, 1, 2, 3


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="cheztui",
        description="A clean, fast TUI for chezmoi. With no command on a terminal, opens the TUI.",
    )
    p.add_argument("--version", action="version", version=f"cheztui {__version__}")
    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    parser.parse_args(argv)
    if not (sys.stdin.isatty() and sys.stdout.isatty()):
        parser.print_help()
        return EXIT_OK
    # Imported here so `--version` and help don't pay for loading Textual.
    from cheztui.tui.app import CheztuiApp

    try:
        CheztuiApp().run()
    except KeyboardInterrupt:
        return 130
    return EXIT_OK
