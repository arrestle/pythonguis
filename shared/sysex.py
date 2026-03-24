"""Ensoniq Mirage parameter SysEx (single-byte value)."""

from __future__ import annotations

import mido

from shared.config import DEVICE_ID, MANUFACTURER_ID


def send_mirage_parameter(midi_port, command_id: int, value: int) -> None:
    """
    Send one parameter change: ``F0 <mfr> <dev> <cmd> <val> F7``.

    ``value`` is masked to 7 bits (0–127); Mirage UI uses lower ranges (e.g. 0–99, 0–31).
    """
    v = int(value) & 0x7F
    data = [MANUFACTURER_ID & 0x7F, DEVICE_ID & 0x7F, int(command_id) & 0x7F, v]
    midi_port.send(mido.Message("sysex", data=data))
