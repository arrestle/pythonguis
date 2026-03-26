"""Runtime diagnostics for troubleshooting (MIDI, versions, platform)."""

from __future__ import annotations

import importlib.metadata
import platform
import sys

import mido
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

from shared.config import MIDI_PORT_NAME


def collect_diagnostics_text(*, opened_output_name: str | None) -> str:
    """Plain-text report suitable for logs or bug reports."""
    lines: list[str] = []
    lines.append("mirage_parm diagnostics")
    lines.append("=" * 52)
    lines.append("")
    lines.append("Environment")
    lines.append(f"  platform: {platform.platform()}")
    lines.append(f"  machine:  {platform.machine()}")
    lines.append(f"  python:   {sys.version.split()[0]}")
    lines.append(f"  exe:      {sys.executable}")
    try:
        lines.append(f"  mido:     {importlib.metadata.version('mido')}")
    except Exception as e:
        lines.append(f"  mido:     (version error: {e})")
    try:
        from PySide6 import __version__ as pyside_ver

        lines.append(f"  PySide6:  {pyside_ver}")
    except Exception as e:
        lines.append(f"  PySide6:  (error: {e})")
    lines.append("")
    lines.append("MIDI (mido)")
    lines.append(f"  shared.config.MIDI_PORT_NAME (substring): {MIDI_PORT_NAME!r}")
    lines.append(f"  opened output port: {opened_output_name!r}")
    lines.append("")
    try:
        outs = mido.get_output_names()
        lines.append(f"  MIDI output ports ({len(outs)}):")
        for n in outs:
            tag = "  <-- current" if opened_output_name and n == opened_output_name else ""
            lines.append(f"    {n}{tag}")
    except Exception as e:
        lines.append(f"  MIDI output ports: (error: {e})")
    lines.append("")
    try:
        ins = mido.get_input_names()
        lines.append(f"  MIDI input ports ({len(ins)}):")
        for n in ins:
            lines.append(f"    {n}")
    except Exception as e:
        lines.append(f"  MIDI input ports: (error: {e})")
    lines.append("")
    lines.append("Notes")
    lines.append("  - Parameter sysex uses the opened output above.")
    lines.append("  - GM preview uses the same port; audio goes to the OS default")
    lines.append("    playback device if the port is a software synth (e.g. GS Wavetable).")
    return "\n".join(lines) + "\n"


def show_diagnostics_dialog(parent: QWidget | None, *, opened_output_name: str | None) -> None:
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
    edit.setPlainText(collect_diagnostics_text(opened_output_name=opened_output_name))
    edit.setFont(QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont))
    layout.addWidget(edit)

    def refresh() -> None:
        edit.setPlainText(collect_diagnostics_text(opened_output_name=opened_output_name))

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
