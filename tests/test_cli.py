"""The command line and the placeholder app."""

import pytest
from textual.widgets import Static

from cheztui import __version__
from cheztui.cli import main
from cheztui.tui.app import CheztuiApp


def test_version(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0
    assert capsys.readouterr().out == f"cheztui {__version__}\n"


async def test_app_starts_and_quits():
    app = CheztuiApp()
    async with app.run_test() as pilot:
        placeholder = app.query_one("#placeholder", Static)
        assert __version__ in str(placeholder.content)
        await pilot.press("q")
    assert app.return_code == 0
