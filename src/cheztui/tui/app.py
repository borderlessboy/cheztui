"""The Textual app. A placeholder until the v0.1 frame lands."""

from __future__ import annotations

from textual.app import App, ComposeResult
from textual.widgets import Footer, Static

from cheztui import __version__


class CheztuiApp(App[None]):
    TITLE = "cheztui"

    CSS = """
    #placeholder {
        width: 1fr;
        height: 1fr;
        content-align: center middle;
    }
    """

    BINDINGS = [("q", "quit", "Quit")]

    def compose(self) -> ComposeResult:
        yield Static(f"cheztui {__version__}: nothing here yet", id="placeholder")
        yield Footer()
