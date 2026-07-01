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

# ---------------------------------------------------------------------------
# §3.1.2 / §3.2.7  Program Dump Request / Response
# ---------------------------------------------------------------------------

_DUMP_REQUEST_LOWER  = 0x03   # PC → Mirage: request lower-keyboard program dump
_DUMP_REQUEST_UPPER  = 0x13   # PC → Mirage: request upper-keyboard program dump
_DUMP_RESPONSE_LOWER = 0x05   # Mirage → PC: lower-keyboard program dump data
_DUMP_RESPONSE_UPPER = 0x15   # Mirage → PC: upper-keyboard program dump data

# Program 1 block starts at byte 481 in the 625-byte decoded dump.
# Maps byte-offset-within-block → Mirage parameter number.
_PROG1_BLOCK_OFFSET = 481
_PROG1_BYTE_TO_PARAM: dict[int, int] = {
    0: 29, 1: 31, 2: 32, 3: 33, 4: 34, 5: 35,
    6: 36, 7: 37, 8: 38,
    10: 27, 11: 28,
    12: 40, 13: 41, 14: 42, 15: 43, 16: 44,
    17: 45, 18: 46, 19: 47, 20: 48, 21: 49,
    22: 50, 23: 51, 24: 52, 25: 53, 26: 54,
    27: 55, 28: 56, 29: 57, 30: 58, 31: 59,
}
# Params where wire value (in dump byte) = display value × divisor.
_WIRE_DIVISOR: dict[int, int] = {36: 2, 37: 2}


def parse_parameter_message(msg_data: tuple) -> "tuple[int, int] | None":
    """
    Parse a §3.2.1 (program) or §3.2.2 (wavesample) message sent by the Mirage.

    These are TRANSMIT-only messages the Mirage sends whenever a parameter changes
    on its front panel.  Format (both types):
        F0 0F 01 <0D|0E> <scope> <param#> <val-LS> <val-MS> F7

    Returns (param_number, display_value) after applying wire→display scaling,
    or None if the message is not a recognised parameter message.
    """
    if len(msg_data) < 7:
        return None
    if msg_data[0] != (MANUFACTURER_ID & 0x7F) or msg_data[1] != (DEVICE_ID & 0x7F):
        return None
    if msg_data[2] not in (0x0D, 0x0E):
        return None
    param_num = msg_data[4]
    wire_value = (msg_data[5] & 0x0F) | ((msg_data[6] & 0x0F) << 4)
    return param_num, wire_value // _WIRE_DIVISOR.get(param_num, 1)


def request_program_dump(midi_port, *, upper: bool = False) -> None:
    """Send §3.1.2 Program Dump Request; Mirage responds with §3.2.7 dump data."""
    msg_type = _DUMP_REQUEST_UPPER if upper else _DUMP_REQUEST_LOWER
    m = mido.Message("sysex", data=[MANUFACTURER_ID & 0x7F, DEVICE_ID & 0x7F, msg_type])
    if _sysex_log_enabled():
        hx = " ".join(f"{b:02X}" for b in bytes(m.bytes()))
        print(f"[mirage sysex] dump request -> {hx}", file=sys.stderr)
    midi_port.send(m)


def receive_program_dump(
    midi_input_port, *, upper: bool = False, timeout: float = 2.0
) -> "dict[int, int] | None":
    """
    Wait up to ``timeout`` seconds for a §3.2.7 Program Dump Data response.

    Returns {param_number: display_value} for Program Parameter Block params (27–59),
    or None if no response arrives within the timeout.
    Wire values for params 36/37 are halved to match the display range.
    """
    expected_type = _DUMP_RESPONSE_UPPER if upper else _DUMP_RESPONSE_LOWER
    deadline = time.time() + timeout
    while time.time() < deadline:
        for msg in midi_input_port.iter_pending():
            if (
                msg.type == "sysex"
                and len(msg.data) >= 4
                and msg.data[0] == (MANUFACTURER_ID & 0x7F)
                and msg.data[1] == (DEVICE_ID & 0x7F)
                and msg.data[2] == expected_type
            ):
                return _parse_program_dump(list(msg.data[3:]))
        time.sleep(0.02)
    return None


def _parse_program_dump(nybbles: list[int]) -> "dict[int, int]":
    """Decode 1250 nybble bytes into 625 raw bytes; extract Program 1 display values."""
    if len(nybbles) < 1250:
        print(
            f"[mirage dump] Short payload: {len(nybbles)} nybbles (expected 1250).",
            file=sys.stderr,
        )
        return {}
    raw = bytearray(625)
    for i in range(625):
        lo = nybbles[i * 2] & 0x0F
        hi = nybbles[i * 2 + 1] & 0x0F
        raw[i] = lo | (hi << 4)
    result: dict[int, int] = {}
    for byte_offset, param_num in _PROG1_BYTE_TO_PARAM.items():
        idx = _PROG1_BLOCK_OFFSET + byte_offset
        if idx < len(raw):
            wire = raw[idx]
            result[param_num] = wire // _WIRE_DIVISOR.get(param_num, 1)
    return result


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
