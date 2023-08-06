from __future__ import annotations
from qtpy.QtWidgets import QMessageBox
from enum import Enum


class MessageBoxMode(Enum):
    ERROR = "error"
    WARNING = "warn"
    INFO = "info"
    QUESTION = "question"
    ABOUT = "about"


_QMESSAGE_MODES = {
    MessageBoxMode.ERROR: QMessageBox.critical,
    MessageBoxMode.WARNING: QMessageBox.warning,
    MessageBoxMode.INFO: QMessageBox.information,
    MessageBoxMode.QUESTION: QMessageBox.question,
    MessageBoxMode.ABOUT: QMessageBox.about,
}


def show_messagebox(
    mode: str | MessageBoxMode = MessageBoxMode.INFO,
    title: str = None,
    text: str = None,
    parent=None,
) -> bool:
    """
    Freeze the GUI and open a messagebox dialog.

    Parameters
    ----------
    mode : str or MessageBoxMode, default is MessageBoxMode.INFO
        Mode of message box. Must be "error", "warn", "info", "question" or "about".
    title : str, optional
        Title of messagebox.
    text : str, optional
        Text in messagebox.
    parent : QWidget, optional
        Parent widget.

    Returns
    -------
    bool
        If "OK" or "Yes" is clicked, return True. Otherwise return False.
    """
    show_dialog = _QMESSAGE_MODES[MessageBoxMode(mode)]
    result = show_dialog(parent, title, text)
    return result in (QMessageBox.Ok, QMessageBox.Yes)
