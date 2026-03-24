"""
Mirage parameter **cards** UI — definitions loaded from **parameter_cards.json**.

Edit ``mirage_parm/parameter_cards.json`` to change labels, parameter numbers (``id``),
ranges (``min``/``max``), or ``kind: "toggle"`` for On/Off. Restart the app to reload.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ParmSpec:
    """One row on a card (from JSON)."""

    label: str
    command_id: int
    min_value: int = 0
    max_value: int = 127
    range_note: str | None = None  # card text e.g. "30-99", "On/Off", "00-FF"


@dataclass(frozen=True)
class PanelSectionSpec:
    """Sub-block inside one card (e.g. ENVELOPE + ENVELOPE MODULATION in one group box)."""

    subtitle: str
    params: tuple[ParmSpec, ...]


@dataclass(frozen=True)
class CardSpec:
    title: str
    description: str
    params: tuple[ParmSpec, ...]
    card_id: str = ""  # JSON "id"; used for main-window row layout
    sections: tuple[PanelSectionSpec, ...] | None = None  # if set, JSON "params" is flattened into params


def _param_from_dict(d: dict[str, Any]) -> ParmSpec:
    cid = int(d["id"])
    label = str(d["label"])
    kind = d.get("kind", "linear")

    if kind == "toggle":
        return ParmSpec(
            label=label,
            command_id=cid,
            min_value=0,
            max_value=1,
            range_note=d.get("range_note", "On/Off"),
        )

    min_v = int(d.get("min", 0))
    max_v = int(d["max"])
    range_note = d.get("range_note")
    if range_note is None:
        range_note = f"{min_v}-{max_v}"
    return ParmSpec(
        label=label,
        command_id=cid,
        min_value=min_v,
        max_value=max_v,
        range_note=str(range_note),
    )


def _card_from_dict(d: dict[str, Any]) -> CardSpec:
    raw_sections = d.get("sections")
    if isinstance(raw_sections, list) and len(raw_sections) > 0:
        section_specs: list[PanelSectionSpec] = []
        flat: list[ParmSpec] = []
        for s in raw_sections:
            if not isinstance(s, dict):
                continue
            subtitle = str(s.get("subtitle", ""))
            sparams = tuple(_param_from_dict(p) for p in s.get("params") or [])
            section_specs.append(PanelSectionSpec(subtitle=subtitle, params=sparams))
            flat.extend(sparams)
        return CardSpec(
            title=str(d["title"]),
            description=str(d.get("description", "")),
            params=tuple(flat),
            card_id=str(d.get("id", "")),
            sections=tuple(section_specs),
        )
    params = tuple(_param_from_dict(p) for p in d.get("params") or [])
    return CardSpec(
        title=str(d["title"]),
        description=str(d.get("description", "")),
        params=params,
        card_id=str(d.get("id", "")),
        sections=None,
    )


def load_cards(path: Path | None = None) -> tuple[CardSpec, ...]:
    """Load card layout from JSON (default: ``parameter_cards.json`` next to this file)."""
    p = path or Path(__file__).with_name("parameter_cards.json")
    raw = json.loads(p.read_text(encoding="utf-8"))
    ver = raw.get("version", 1)
    if ver != 1:
        raise ValueError(f"Unsupported parameter_cards.json version: {ver!r}")
    cards = raw.get("cards")
    if not isinstance(cards, list):
        raise ValueError("parameter_cards.json: missing 'cards' array")
    return tuple(_card_from_dict(c) for c in cards)


CARDS: tuple[CardSpec, ...] = load_cards()
