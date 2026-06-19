"""Runtime diagnostics for troubleshooting (MIDI, versions, platform)."""

from __future__ import annotations

from PySide6.QtGui import QFontDatabase, QGuiApplication
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from shared.diagnostics_report import collect_diagnostics_text

__all__ = ["collect_diagnostics_text", "show_diagnostics_dialog"]


def show_diagnostics_dialog(
    parent: QWidget | None,
    *,
    opened_output_name: str | None,
    opened_echo_output_name: str | None = None,
) -> None:
    """Modal dialog with copyable diagnostics text."""

    dlg = QDialog(parent)
    dlg.setWindowTitle("Diagnostics — mirage_parm")
    dlg.setMinimumSize(580, 440)

    layout = QVBoxLayout(dlg)
    hint = QLabel(
        "Copy this text when reporting MIDI or install issues. "
        "Use Refresh to re-read the current port list from the OS."
    )
    hint.setWordWrap(True)
    layout.addWidget(hint)

    edit = QPlainTextEdit()
    edit.setReadOnly(True)
    edit.setPlainText(
        collect_diagnostics_text(
            opened_output_name=opened_output_name,
            opened_echo_output_name=opened_echo_output_name,
        )
    )
    edit.setFont(QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont))
    layout.addWidget(edit)

    def refresh() -> None:
        edit.setPlainText(
            collect_diagnostics_text(
                opened_output_name=opened_output_name,
                opened_echo_output_name=opened_echo_output_name,
            )
        )

    btn_row = QHBoxLayout()
    refresh_btn = QPushButton("Refresh")
    refresh_btn.clicked.connect(refresh)
    btn_row.addWidget(refresh_btn)
    btn_row.addStretch(1)
    layout.addLayout(btn_row)

    button_box = QDialogButtonBox()
    copy_pb = button_box.addButton(
        "Copy to clipboard", QDialogButtonBox.ButtonRole.ActionRole
    )
    copy_pb.clicked.connect(lambda: QGuiApplication.clipboard().setText(edit.toPlainText()))
    close_pb = button_box.addButton(QDialogButtonBox.StandardButton.Close)
    close_pb.clicked.connect(dlg.accept)
    layout.addWidget(button_box)

    dlg.exec()
