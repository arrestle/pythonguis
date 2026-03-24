"""MIDI port discovery (mido)."""

from __future__ import annotations

from typing import Any

import mido


def open_midi_output_port(port_name_substring: str) -> tuple[Any, str]:
    """
    Open the first MIDI output whose name contains ``port_name_substring``.

    Returns ``(port, matched_name)``. Caller should close the port when done if desired.
    """
    available_ports = mido.get_output_names()
    print("Available MIDI Output Ports:", available_ports)

    for name in available_ports:
        if port_name_substring in name:
            return mido.open_output(name), name

    raise RuntimeError(
        f"No available MIDI output port matching {port_name_substring!r}."
    )
