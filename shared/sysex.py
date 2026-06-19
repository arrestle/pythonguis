"""Ensoniq Mirage parameter SysEx (Advanced Samplers Guide §3.2.1 / §3.2.2)."""

from __future__ import annotations

import os
import sys
from typing import Any, Literal

import mido

from shared.config import (
    DEVICE_ID,
    MANUFACTURER_ID,
    MIRAGE_PROGRAM_SELECT,
    MIRAGE_SYSEX_LOG,
    MIRAGE_UPPER_KEYBOARD,
    MIRAGE_WAVESAMPLE_SELECT,
)


def _sysex_log_enabled() -> bool:
    ev = os.environ.get("MIRAGE_SYSEX_LOG")
    if ev is not None:
        return ev.strip().lower() in ("1", "true", "yes", "on")
    return bool(MIRAGE_SYSEX_LOG)

# Message type bytes (transmit format; same layout used for remote control).
_SYSEX_PROGRAM_PARAMETER = 0x0D  # §3.2.1 Program parameter message
_SYSEX_WAVESAMPLE_PARAMETER = 0x0E  # §3.2.2 Wavesample parameter message


def _encode_value_nybble_bytes(value: int) -> tuple[int, int]:
    """
    Value as LS nybble byte then MS nybble byte (§3.2.1 / §3.2.2; 0–255).
    Each MIDI data byte carries one hex digit in bits 0–3 (OOO0O0VVVV style).
    """
    v = max(0, int(value)) & 0xFF
    ls = v & 0x0F
    ms = (v >> 4) & 0x0F
    return ls, ms


def _program_keyboard_byte(
    *, upper: bool | None = None, program: int | None = None
) -> int:
    """OUONOOPP byte: N (upper) in bit 6, PP = program 0–3 in bits 0–1."""
    u = MIRAGE_UPPER_KEYBOARD if upper is None else upper
    pp = MIRAGE_PROGRAM_SELECT if program is None else int(program)
    n_bit = 1 if u else 0
    return (n_bit << 6) | (pp & 0x03)


def _wavesample_scope_byte(
    *, upper: bool | None = None, wavesample: int | None = None
) -> int:
    """OOONOSSS-style byte: N in bit 6, SSS = wavesample 0–7 in bits 0–2."""
    u = MIRAGE_UPPER_KEYBOARD if upper is None else upper
    w = MIRAGE_WAVESAMPLE_SELECT if wavesample is None else int(wavesample)
    n_bit = 1 if u else 0
    return (n_bit << 6) | (w & 0x07)


def send_mirage_parameter(
    midi_port,
    parameter_number: int,
    value: int,
    *,
    kind: Literal["program", "wavesample"] = "program",
    echo_port: Any | None = None,
) -> None:
    """
    Send one parameter change.

    Program parameters (``kind="program"``): ``F0 0F 01 0D <kbd/prog> <param#> <val LS> <val MS> F7``.

    Wavesample parameters (``kind="wavesample"``): ``F0 0F 01 0E <scope> <param#> <val LS> <val MS> F7``.

    ``parameter_number`` is the Mirage parameter index (same as card ``id`` / front-panel number).
    Keyboard/program and wavesample indices come from ``shared.config``.

    If ``echo_port`` is set (e.g. MIDI-OX virtual cable), the same SysEx is sent there too.
    """
    param = int(parameter_number) & 0x7F
    v_lo, v_hi = _encode_value_nybble_bytes(value)

    if kind == "wavesample":
        scope = _wavesample_scope_byte()
        msg_type = _SYSEX_WAVESAMPLE_PARAMETER
    else:
        scope = _program_keyboard_byte()
        msg_type = _SYSEX_PROGRAM_PARAMETER

    data = [
        MANUFACTURER_ID & 0x7F,
        DEVICE_ID & 0x7F,
        msg_type,
        scope & 0x7F,
        param,
        v_lo & 0x7F,
        v_hi & 0x7F,
    ]
    msg = mido.Message("sysex", data=data)
    if _sysex_log_enabled():
        raw = bytes(msg.bytes())
        hx = " ".join(f"{b:02X}" for b in raw)
        print(
            f"[mirage sysex] kind={kind!r} param={parameter_number} value={value} "
            f"scope=0x{scope & 0x7F:02X} -> {hx}",
            file=sys.stderr,
        )
    midi_port.send(msg)
    if echo_port is not None:
        echo_port.send(mido.Message("sysex", data=data))
