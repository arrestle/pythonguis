"""Ensoniq Mirage parameter SysEx — MASOS §3.1.1 command-code: param-select + UP/DOWN arrows."""

from __future__ import annotations

import os
import sys
import time
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
_CMD_END = 0x7F  # end-of-command marker

# §3.1.1 Keypad codes (Table 3.3 in MASOS MIDI implementation spec).
_KEY_PARAM = 0x0C  # PARAM button — enters parameter-select mode
_KEY_ENTER = 0x0E  # ENTER / UP-ARROW  (increments value when in value-view mode)
_KEY_DOWN  = 0x0F  # CANCEL / DOWN-ARROW (decrements value when in value-view mode)

# NOTE: 0x0D (Program Parameter) and 0x0E (Wavesample Parameter) are §3.2 *Transmit*
# messages — the Mirage sends those to the PC when the user edits the front panel.
# They are NOT valid receive commands; the Mirage ignores them as input.

# NOTE on ENTER/UP-ARROW audio: the Mirage plays a brief audition note each time a
# value is incremented — this is intentional hardware behaviour, not a bug.


def send_mirage_parameter(
    midi_port,
    parameter_number: int,
    value: int,
    *,
    previous_value: int | None = None,
    min_value: int = 0,
    max_value: int = 127,
    mode: Literal["delta", "absolute"] = "delta",
    kind: Literal["program", "wavesample"] = "program",
    echo_port: Any | None = None,
) -> None:
    """
    Set one Mirage parameter via §3.1.1 MASOS front-panel command code simulation.

     Sends command-code SysEx messages:
      1. Param select:  F0 0F 01 01  0C <param digits> 0E  7F F7
         (PARAM → <number> → ENTER, max 4 keypad bytes, within the 5-byte limit)
        2. Value movement using UP/DOWN arrows:
            - mode="delta": abs(value-previous_value) steps
            - mode="absolute": force to min then step up to target
         (ENTER = UP-ARROW, CANCEL = DOWN-ARROW, one press per step)

    ``previous_value`` is the value that was last sent to the Mirage for this parameter.
     In ``mode="delta"``, the delta between ``previous_value`` and ``value`` determines
     steps. If ``previous_value`` is None, only parameter-select is sent.
     In ``mode="absolute"``, ``min_value``/``max_value`` are used to anchor at min then
     walk up to the target. This is slower but robust if the Mirage drops rapid steps.

    ``kind`` is accepted for API compatibility but unused — the Mirage determines
    program-vs-wavesample context from the parameter number and its own current state.

    If ``echo_port`` is set, the same SysEx is mirrored there (e.g. for MIDI-OX).
    """
    log = _sysex_log_enabled()

    def _send(data: list[int]) -> None:
        m = mido.Message("sysex", data=data)
        if log:
            hx = " ".join(f"{b:02X}" for b in bytes(m.bytes()))
            print(f"[mirage sysex] -> {hx}", file=sys.stderr)
        midi_port.send(m)
        if echo_port is not None:
            echo_port.send(mido.Message("sysex", data=data))

    def _press(key: int, count: int) -> None:
        if count <= 0:
            return
        # Small pacing delay avoids dropped increments on Mirage command-code input.
        for _ in range(count):
            _send(hdr + [key, _CMD_END])
            time.sleep(0.012)

    hdr = [MANUFACTURER_ID & 0x7F, DEVICE_ID & 0x7F, _CMD_CODE_MSG_TYPE]

    # 1. Parameter select: PARAM + digits + ENTER  (≤4 keypad bytes, within 5-byte limit)
    param_digits = [int(d) for d in str(int(parameter_number))]
    select_data = hdr + [_KEY_PARAM] + param_digits + [_KEY_ENTER, _CMD_END]
    if log:
        print(
            f"[mirage sysex] kind={kind!r} param={parameter_number} value={value} "
            f"prev={previous_value}",
            file=sys.stderr,
        )
    _send(select_data)

    # 2. Value movement
    v = int(value)
    lo = int(min_value)
    hi = int(max_value)
    if v < lo:
        v = lo
    if v > hi:
        v = hi

    if mode == "absolute":
        # Anchor to minimum (guaranteed by over-stepping downward), then walk up.
        _press(_KEY_DOWN, hi - lo)
        _press(_KEY_ENTER, v - lo)
        return

    if previous_value is not None:
        delta = v - int(previous_value)
        arrow = _KEY_ENTER if delta >= 0 else _KEY_DOWN  # 0x0E = UP, 0x0F = DOWN
        _press(arrow, abs(delta))
