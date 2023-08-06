# from __future__ import annotations
from pathlib import Path
from typing import Callable, List, TYPE_CHECKING, Union
import weakref
from qtpy import QtWidgets as QtW, QtCore
from qtpy.QtWidgets import QAction

from ._svg import QColoredSVGIcon
from ._multitips import QHasToolTip
from ._history import QtFileHistoryManager
from . import _dialogs as _dlg


if TYPE_CHECKING:
    from ._mainwindow import _QtMainWidgetBase
    from ..widgets.mainwindow import TableViewerBase

SUMMARY_CHOICES = ["mean", "median", "std", "sem", "min", "max", "sum"]

ICON_DIR = Path(__file__).parent / "_icons"


class _QToolBar(QtW.QToolBar, QHasToolTip):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._button_and_icon: List["tuple[QtW.QToolButton, QColoredSVGIcon]"] = []

    def updateIconColor(self, color):
        for button, icon in self._button_and_icon:
            button.setIcon(icon.colored(color))

    def appendAction(self, f: Callable, qicon: "QColoredSVGIcon"):
        action = self.addAction(qicon, "")
        action.triggered.connect(f)
        action.setToolTip(f.__doc__)
        btn = self.widgetForAction(action)
        self._button_and_icon.append((btn, qicon))
        return None

    def toolTipPosition(self, index: int) -> QtCore.QPoint:
        btn, icon = self._button_and_icon[index]
        pos = btn.pos()
        pos.setY(pos.y() + btn.height() // 2)
        return pos

    def toolTipCount(self) -> int:
        return len(self._button_and_icon)

    def clickButton(self, index: int, *, ignore_index_error: bool = True):
        """Emulate a click on the button at the given index."""
        if index < 0 or index >= len(self._button_and_icon):
            if ignore_index_error:
                return None
            else:
                raise IndexError(f"Index {index} out of range")
        btn, icon = self._button_and_icon[index]
        return btn.click()


class QTableStackToolBar(QtW.QToolBar, QHasToolTip):
    _hist_mgr = QtFileHistoryManager()

    def __init__(self, parent: "_QtMainWidgetBase"):
        super().__init__(parent)

        self._tab = QtW.QTabWidget(self)
        self._tab.setContentsMargins(0, 0, 0, 0)
        self._tab.setStyleSheet(
            r"QTabWidget {margin: 0px, 0px, 0px, 0px; padding: 0px;}"
        )
        self._child_widgets: weakref.WeakValueDictionary[
            str, _QToolBar
        ] = weakref.WeakValueDictionary()

        self.addWidget(self._tab)
        self.setMaximumHeight(120)

        # Add tool buttons
        # fmt: off
        self.registerAction("File", self.open_table, ICON_DIR / "open_table.svg")
        self.registerAction("File", self.open_spreadsheet, ICON_DIR / "open_spreadsheet.svg")
        self.registerAction("File", self.save_table, ICON_DIR / "save_table.svg")

        self.registerAction("Table", self.copy_as_table, ICON_DIR / "copy_as_table.svg")
        self.registerAction("Table", self.copy_as_spreadsheet, ICON_DIR / "copy_as_spreadsheet.svg")
        self.registerAction("Table", self.new_spreadsheet, ICON_DIR / "new_spreadsheet.svg")
        self.addSeparatorToChild("Table")
        self.registerAction("Table", self.groupby, ICON_DIR / "groupby.svg")
        self.registerAction("Table", self.hconcat, ICON_DIR / "hconcat.svg")
        self.registerAction("Table", self.vconcat, ICON_DIR / "vconcat.svg")
        self.registerAction("Table", self.pivot, ICON_DIR / "pivot.svg")
        self.registerAction("Table", self.melt, ICON_DIR / "melt.svg")
        self.addSeparatorToChild("Table")
        self.registerAction("Table", self.query, ICON_DIR / "query.svg")

        self.registerAction("Analyze", self.summarize_table, ICON_DIR / "summarize_table.svg")
        self.registerAction("Analyze", self.toggle_console, ICON_DIR / "toggle_console.svg")
        self.addSeparatorToChild("Analyze")
        # fmt: on

    @property
    def viewer(self) -> "TableViewerBase":
        """The parent viewer object."""
        return self.parent()._table_viewer

    def currentIndex(self) -> int:
        """Current tab index."""
        return self._tab.currentIndex()

    def setCurrentIndex(self, index: int):
        """Set current tab index."""
        return self._tab.setCurrentIndex(index)

    def currentToolBar(self) -> _QToolBar:
        """Current toolbar."""
        return self._child_widgets[self._tab.tabText(self._tab.currentIndex())]

    def toolTipPosition(self, index: int) -> QtCore.QPoint:
        return self._tab.tabBar().tabRect(index).topLeft()

    def toolTipText(self, index: int) -> str:
        return list(self._child_widgets.keys())[index][0]

    def toolTipCount(self) -> int:
        return self._tab.count()

    if TYPE_CHECKING:

        def parent(self) -> "_QtMainWidgetBase":
            ...

    def addToolBar(self, name: str):
        """Add a tab of toolbar of name ``name``."""
        if name in self._child_widgets.keys():
            raise ValueError(f"Tab with name {name!r} already exists.")
        toolbar = _QToolBar(self)
        toolbar.setContentsMargins(0, 0, 0, 0)
        self._tab.addTab(toolbar, name)
        self._child_widgets[name] = toolbar

    def registerAction(self, tabname: str, f: Callable, icon: Union[str, Path]):
        """Register a callback `f` in tab `tabname`."""
        if tabname not in self._child_widgets:
            self.addToolBar(tabname)
        toolbar = self._child_widgets[tabname]
        qicon = QColoredSVGIcon.fromfile(str(icon))
        toolbar.appendAction(f, qicon)
        return None

    def addSeparatorToChild(self, tabname: str) -> QAction:
        toolbar = self._child_widgets[tabname]
        return toolbar.addSeparator()

    def setToolButtonColor(self, color: str):
        """Update all the tool button colors."""
        for toolbar in self._child_widgets.values():
            toolbar.updateIconColor(color)

    def open_table(self):
        """Open a file as a table."""
        return self._open(type="table")

    def open_spreadsheet(self):
        """Open a file as a spreadsheet."""
        return self._open(type="spreadsheet")

    def _open(self, type):
        paths = self._hist_mgr.openFileDialog(mode="rm", caption="Open file(s)")
        for path in paths:
            self.viewer.open(path, type=type)
        return None

    def save_table(self):
        """Save current table."""
        path = self._hist_mgr.openFileDialog(mode="w", caption="Save table")
        if path:
            self.viewer.save(path)
        return None

    def copy_as_table(self):
        """Make a copy of the current table."""
        viewer = self.viewer
        table = viewer.current_table
        if table is not None:
            viewer.add_table(table.data, name=f"{table.name}-copy")

    def copy_as_spreadsheet(self):
        """Make a copy of the current table."""
        viewer = self.viewer
        table = viewer.current_table
        if table is not None:
            viewer.add_spreadsheet(table.data, name=f"{table.name}-copy")

    def new_spreadsheet(self):
        """Create a new spreadsheet."""
        self.viewer.add_spreadsheet(name="New")

    def groupby(self):
        """Group table data by its column value."""
        table = self.viewer.current_table
        if table is not None:
            out = _dlg.groupby(
                df={"bind": table.data},
                by={"choices": list(table.data.columns), "widget_type": "Select"},
            )
            if out is not None:
                self.viewer.add_groupby(out, name=f"{table.name}-groupby")

    def hconcat(self):
        """Concatenate tables horizontally."""
        out = _dlg.hconcat(
            viewer={"bind": self.viewer},
            names={
                "value": [self.viewer.current_table.name],
                "widget_type": "Select",
                "choices": [t.name for t in self.viewer.tables],
            },
        )
        if out is not None:
            self.viewer.add_table(out, name=f"hconcat")

    def vconcat(self):
        """Concatenate tables vertically."""
        out = _dlg.vconcat(
            viewer={"bind": self.viewer},
            names={
                "value": [self.viewer.current_table.name],
                "widget_type": "Select",
                "choices": [t.name for t in self.viewer.tables],
            },
        )
        if out is not None:
            self.viewer.add_table(out, name=f"vconcat")

    def pivot(self):
        """Pivot a table."""
        table = self.viewer.current_table
        if table is None:
            return
        col = list(table.data.columns)
        if len(col) < 3:
            raise ValueError("Table must have at least three columns.")
        out = _dlg.pivot(
            df={"bind": table.data},
            index={"choices": col, "value": col[0]},
            columns={"choices": col, "value": col[1]},
            values={"choices": col, "value": col[2]},
        )
        if out is not None:
            self.viewer.add_table(out, name=f"{table.name}-pivot")

    def melt(self):
        """Unpivot a table."""
        table = self.viewer.current_table
        if table is None:
            return
        out = _dlg.melt(
            df={"bind": table.data},
            id_vars={"choices": list(table.data.columns), "widget_type": "Select"},
        )
        if out is not None:
            self.viewer.add_table(out, name=f"{table.name}-melt")

    def summarize_table(self):
        """Summarize current table."""
        table = self.viewer.current_table
        if table is None:
            return
        out = _dlg.summarize_table(
            df={"bind": table.data},
            methods={"choices": SUMMARY_CHOICES, "widget_type": "Select"},
        )
        if out is not None:
            self.viewer.add_table(out, name=f"{table.name}-summary")

    def toggle_console(self):
        """Toggle embedded console."""
        return self.parent().toggleConsoleVisibility()

    def query(self):
        """Filter table using a query."""
        table = self.viewer.current_table
        if table is None:
            return
        out = _dlg.query(df={"bind": table.data})
        if out is not None:
            self.viewer.add_table(out, name=f"{table.name}-query")
