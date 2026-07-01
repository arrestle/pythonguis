"""MIDI port discovery (mido)."""

from __future__ import annotations

import sys
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
            print(f"Using MIDI output: {name!r} (matched {port_name_substring!r})")
            return mido.open_output(name), name

    raise RuntimeError(
        f"No available MIDI output port matching {port_name_substring!r}."
    )


def open_midi_input_port_optional(port_name_substring: str) -> tuple[Any | None, str | None]:
    """
    Open the first MIDI input whose name contains ``port_name_substring``.
    Returns (port, matched_name) or (None, None) if not found or substring is empty.
    Used to receive the §3.2.7 Program Dump Data response on startup.
    """
    s = (port_name_substring or "").strip()
    if not s:
        return None, None
    available_ports = mido.get_input_names()
    print("Available MIDI Input Ports:", available_ports)
    for name in available_ports:
        if s in name:
            print(f"Using MIDI input: {name!r} (matched {s!r})")
            return mido.open_input(name), name
    print(
        f"MIDI input: no port matching {s!r}; program dump sync disabled. "
        f"Available: {available_ports}",
        file=sys.stderr,
    )
    return None, None


def open_midi_output_port_optional(port_name_substring: str) -> tuple[Any | None, str | None]:
    """
    Open a second MIDI output if ``port_name_substring`` is non-empty; otherwise (None, None).

    Used to mirror SysEx to a virtual port (e.g. loopMIDI) for MIDI-OX while the primary
    port goes to the Mirage. On no match, prints a warning and returns (None, None).
    """
    s = (port_name_substring or "").strip()
    if not s:
        return None, None
    available_ports = mido.get_output_names()
    for name in available_ports:
        if s in name:
            print(f"MIDI echo output: {name!r} (matched {s!r})")
            return mido.open_output(name), name
    print(
        f"MIDI echo: no output port matching {s!r}; continuing without echo. "
        f"Available: {available_ports}",
        file=sys.stderr,
    )
    return None, None
