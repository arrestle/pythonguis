"""Plain-text diagnostics (no Qt); safe for logging and stdout."""

from __future__ import annotations

import importlib.metadata
import os
import platform
import sys

import mido

from shared.config import (
    MIDI_ECHO_PORT_NAME,
    MIDI_PORT_NAME,
    MIRAGE_DEFAULT_PARAMETER_NUMBER,
    MIRAGE_PROGRAM_SELECT,
    MIRAGE_SYSEX_LOG,
    MIRAGE_UPPER_KEYBOARD,
    MIRAGE_WAVESAMPLE_SELECT,
)


def collect_diagnostics_text(
    *,
    opened_output_name: str | None,
    opened_echo_output_name: str | None = None,
) -> str:
    """Plain-text report suitable for logs, terminal, or bug reports."""
    lines: list[str] = []
    lines.append("MIDI / runtime diagnostics")
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
    lines.append(
        f"  shared.config.MIDI_ECHO_PORT_NAME (SysEx mirror): {MIDI_ECHO_PORT_NAME!r}"
    )
    lines.append(f"  opened echo output port: {opened_echo_output_name!r}")
    lines.append(f"  MIRAGE_UPPER_KEYBOARD: {MIRAGE_UPPER_KEYBOARD!r}")
    lines.append(f"  MIRAGE_PROGRAM_SELECT: {MIRAGE_PROGRAM_SELECT!r}")
    lines.append(f"  MIRAGE_WAVESAMPLE_SELECT: {MIRAGE_WAVESAMPLE_SELECT!r}")
    lines.append(
        f"  MIRAGE_DEFAULT_PARAMETER_NUMBER (reference / tests): {MIRAGE_DEFAULT_PARAMETER_NUMBER!r}"
    )
    ev = os.environ.get("MIRAGE_SYSEX_LOG")
    sysex_log = (
        ev.strip().lower() in ("1", "true", "yes", "on")
        if ev is not None
        else bool(MIRAGE_SYSEX_LOG)
    )
    lines.append(f"  MIRAGE_SYSEX_LOG (hex to stderr): {sysex_log!r}")
    if ev is not None:
        lines.append(f"    (env MIRAGE_SYSEX_LOG={ev!r} overrides config)")
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
    lines.append(
        "  - Parameter SysEx: §3.2.1 (program) / §3.2.2 (wavesample); "
        "see shared/sysex.py and MIRAGE_* settings above."
    )
    lines.append("  - Parameter sysex uses the opened output above.")
    lines.append("  - GM preview uses the same port; audio goes to the OS default")
    lines.append("    playback device if the port is a software synth (e.g. GS Wavetable).")
    lines.append("")
    lines.append("Troubleshooting (no sound / no parameter change)")
    lines.append(
        "  1) Turn on hex logging: set env MIRAGE_SYSEX_LOG=1 or "
        "MIRAGE_SYSEX_LOG = True in shared/config.py; move one slider and "
        "compare the line to MIDI-OX / a Mirage front-panel edit (same param)."
    )
    lines.append(
        "  2) Cabling: PC MIDI OUT -> Mirage MIDI IN (this app only sends on an OUTPUT port)."
    )
    lines.append(
        "  3) Match scope: MIRAGE_UPPER_KEYBOARD / MIRAGE_PROGRAM_SELECT / "
        "MIRAGE_WAVESAMPLE_SELECT must match the program side and wavesample "
        "you are editing on the Mirage."
    )
    lines.append(
        "  4) Card kind: wavesample cards use message type 0x0E; others use 0x0D. "
        "Override with \"sysex\" in parameter_cards.json if needed."
    )
    lines.append(
        "  5) Manual §3.2 footnote: Mirage->computer dumps may require "
        "External Computer Port (parameter [91]); confirm in Advanced Samplers Guide "
        "for your OS version if the Mirage ignores inbound SysEx."
    )
    lines.append(
        "  6) MIDI-OX monitor: create a virtual MIDI port (e.g. loopMIDI), set "
        "MIDI_ECHO_PORT_NAME in shared/config.py to match that OUTPUT name; "
        "in MIDI-OX open that port as INPUT — duplicate SysEx is sent there."
    )
    return "\n".join(lines) + "\n"
