"""Ensoniq Mirage parameter SysEx — MASOS front-panel command code (§3.1.1 receive format)."""

from __future__ import annotations

import os
import sys
from typing import Any, Literal

import mido

from shared.config import (
    DEVICE_ID,
    MANUFACTURER_ID,
    MIRAGE_SYSEX_LOG,
)


def _sysex_log_enabled() -> bool:
    ev = os.environ.get("MIRAGE_SYSEX_LOG")
    if ev is not None:
        return ev.strip().lower() in ("1", "true", "yes", "on")
    return bool(MIRAGE_SYSEX_LOG)

# §3.1.1 Mirage Command Code message type (receive — simulates front-panel keypresses).
_CMD_CODE_MSG_TYPE = 0x01
# §3.1.1 Keypad codes (Table 3.3 in MASOS MIDI implementation spec).
_KEY_PARAM  = 0x0C  # PARAM button
_KEY_VALUE  = 0x0D  # VALUE button
_KEY_ENTER  = 0x0E  # ENTER button
_KEY_UP     = 0x0E  # UP-ARROW (same byte as ENTER in OCR'd table; both 0x0E)
_KEY_DOWN   = 0x0F  # DOWN-ARROW / CANCEL
_CMD_END    = 0x7F  # End-of-command marker

# NOTE: 0x0D (Program Parameter) and 0x0E (Wavesample Parameter) are §3.2 *Transmit*
# messages — the Mirage sends those to the PC when the user edits the front panel.
# They are NOT valid receive commands; the Mirage ignores them as input.
# Use §3.1.1 command-code simulation (above) to set parameters from the PC.


def send_mirage_parameter(
    midi_port,
    parameter_number: int,
    value: int,
    *,
    kind: Literal["program", "wavesample"] = "program",
    echo_port: Any | None = None,
) -> None:
    """
    Set one Mirage parameter via §3.1.1 MASOS front-panel command code simulation.

    Sends:  F0 0F 01 01 [PARAM] [param digits] [VALUE] [value digits] [ENTER] 7F F7

    This simulates the user pressing PARAM → <number> → VALUE → <number> → ENTER on
    the Mirage keypad.  It is the only documented *receive* path for changing individual
    parameters via SysEx; the 0x0D/0x0E messages are §3.2 *transmit-only* (Mirage→PC).

    ``kind`` is accepted for API compatibility but is not used in the message — the Mirage
    determines program-vs-wavesample from the parameter number and its own current state.

    If ``echo_port`` is set, the same SysEx is mirrored there (e.g. for MIDI-OX).
    """
    param_digits = [int(d) for d in str(int(parameter_number))]
    val_digits   = [int(d) for d in str(max(0, int(value)))]
    keypad = [_KEY_PARAM] + param_digits + [_KEY_VALUE] + val_digits + [_KEY_ENTER]

    data = [
        MANUFACTURER_ID & 0x7F,
        DEVICE_ID & 0x7F,
        _CMD_CODE_MSG_TYPE,
        *keypad,
        _CMD_END,
    ]
    msg = mido.Message("sysex", data=data)
    if _sysex_log_enabled():
        raw = bytes(msg.bytes())
        hx = " ".join(f"{b:02X}" for b in raw)
        print(
            f"[mirage sysex] kind={kind!r} param={parameter_number} value={value} "
            f"-> {hx}",
            file=sys.stderr,
        )
    midi_port.send(msg)
    if echo_port is not None:
        echo_port.send(mido.Message("sysex", data=data))
