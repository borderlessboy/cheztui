"""The list and detail panes every view fills (spec §4; DEC-2)."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import ClassVar, Generic, TypeVar

from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Container, Vertical, VerticalScroll
from textual.widgets import OptionList, Static
from textual.widgets.option_list import Option

from cheztui.tui.keys import Key

Row = TypeVar("Row")


class RowList(OptionList, inherit_bindings=False):
    """The list pane. Its keys are the app's (spec §5 Keys), so it has none of its own."""


class Detail(VerticalScroll, inherit_bindings=False):
    """The detail pane; it scrolls on the app's keys."""


class ListDetail(Container, Generic[Row]):
    """A list of rows keyed by target, and the current row's detail.

    The rows are `None` before the view's read succeeds (blank), or a
    sequence, empty when there's nothing to list; `message` replaces them
    with a line such as a read's error.
    """

    NAME: ClassVar[str] = ""
    KEYS: ClassVar[tuple[Key, ...]] = ()
    EMPTY: ClassVar[str] = ""  # the one line shown with no rows

    def __init__(self, *, id: str | None = None) -> None:
        super().__init__(id=id)
        self.rows: tuple[Row, ...] | None = None
        self.message: str | None = None

    # What a view says about its rows.

    def key(self, row: Row) -> Path:
        raise NotImplementedError

    def label(self, row: Row) -> str:
        raise NotImplementedError

    def detail(self, row: Row) -> str:
        raise NotImplementedError

    # The panes.

    def compose(self) -> ComposeResult:
        with Container(id="panes"):
            with Vertical(id="list-pane"):
                yield RowList(id="list")
                yield Static(id="list-message", markup=False)
            with Detail(id="detail"):
                yield Static(id="detail-body", markup=False)

    @property
    def count(self) -> int | None:
        """The rows to show on the view's tab, or None for no count (spec §4 Tab label)."""
        return len(self.rows) if self.rows else None

    def show_rows(self, rows: Sequence[Row]) -> None:
        self.rows, self.message = tuple(rows), None
        self._render_rows()

    def show_message(self, message: str | None) -> None:
        """Replace the rows with `message`, or with nothing at all when it's None."""
        self.rows, self.message = None, message
        self._render_rows()

    def current(self) -> Row | None:
        if not self.rows:
            return None
        index = self.query_one(RowList).highlighted
        return self.rows[index] if index is not None else None

    def _render_rows(self) -> None:
        rows = self.rows or ()
        listing = self.query_one(RowList)
        listing.clear_options()
        listing.add_options(Option(Text(self.label(r)), id=str(self.key(r))) for r in rows)
        if rows:
            listing.highlighted = 0
        text = self.message if self.message is not None else self.EMPTY if self.rows == () else ""
        self.query_one("#list-message", Static).update(text)
        self.set_class(not rows, "-no-rows")
        self._render_detail()

    def _render_detail(self) -> None:
        row = self.current()
        self.query_one("#detail-body", Static).update("" if row is None else self.detail(row))

    def on_option_list_option_highlighted(self, event: OptionList.OptionHighlighted) -> None:
        event.stop()
        self._render_detail()
