---
name: mirage-parm-ui
description: 'PySide6 UI layer for the Mirage parameter editor. Use when: adding or renaming parameters, changing card layout, fixing slider/spinbox behaviour, modifying panel colours, adding a new card to the main window, debugging why a widget sends wrong values, or working on mirage_parm/main.py, mirage_parm/widgets.py, mirage_parm/parameters.py, or mirage_parm/parameter_cards.json.'
argument-hint: 'Describe the UI or layout issue'
---

# Mirage Parm UI — Project Knowledge

## Key Files

| File | Role |
|------|------|
| [mirage_parm/main.py](../../../../mirage_parm/main.py) | `MainWindow`: card rows, panel layout, QSS styles |
| [mirage_parm/widgets.py](../../../../mirage_parm/widgets.py) | `ParmRow` (slider/spinbox/buttons) + `ParameterCard` (group box) |
| [mirage_parm/parameters.py](../../../../mirage_parm/parameters.py) | JSON → `CardSpec`/`ParmSpec` dataclasses; sysex_kind derivation |
| [mirage_parm/parameter_cards.json](../../../../mirage_parm/parameter_cards.json) | Single source of truth for parameter labels, IDs, and ranges |
| [shared/sysex.py](../../../../shared/sysex.py) | SysEx send logic (called by `ParmRow._send_value`) |
| [shared/config.py](../../../../shared/config.py) | MIDI port name, device ID, upper/lower, program, wavesample |

## How Parameters Are Defined

Edit **`parameter_cards.json`** — restart the app to reload. Each parameter entry:

```json
{ "id": 36, "label": "Filter Cutoff Freq", "max": 99 }
```

- `"id"` → `ParmSpec.command_id` (sent in SysEx)
- `"min"` defaults to `0`; `"max"` is required
- `"kind": "toggle"` → forces `min=0, max=1`, `range_note="On/Off"`
- `"sysex": "wavesample"` overrides the per-card default (cards whose `id` contains `"wavesample"` default to `"wavesample"`; all others default to `"program"`)
- `"range_note"` sets tooltip text on the label and slider; auto-generated as `"{min}-{max}"` if omitted

Cards can be flat (`"params": [...]`) or sectioned (`"sections": [{"subtitle": "...", "params": [...]}]`).

## Card Layout in the Main Window

`main.py` hard-codes two coloured panels:

| Panel | Row 1 card IDs | Row 2 card IDs |
|-------|---------------|---------------|
| **Red** | `sampling`, `sampling_config`, `command` | `configuration`, `wavesample_sampling` |
| **Yellow** | `program`, `keyboard_program`, `general_keyboard` | `wavesample_program`, `envelope` |

Cards not in either panel are appended below as unstyled default cards.

To **add a new card** to an existing panel row, add its `card_id` to the appropriate tuple constant (`_RED_PANEL_ROW1`, etc.) in `main.py` and add a corresponding entry in `parameter_cards.json`.

### Special card IDs

| card_id | Widget behaviour |
|---------|-----------------|
| `sampling`, `program` | Narrow (`≤220 px`), top-aligned, "Play test MIDI" button shown |
| `envelope` | Two-column FILTER / AMPLITUDE split via `_add_envelope_filter_amplitude_columns` |
| `wavesample_program` | Single narrow column (`≤400 px`), slim yellow QSS name |
| `sampling_config`, `command`, `configuration` | 2-column reference card grid |
| `wavesample_sampling` | 3-column reference card grid |
| `keyboard_program`, `general_keyboard` | 2-column reference card grid |

Column counts are in `_REFERENCE_CARD_COLUMN_COUNTS` (widgets.py:296).

## Widget Send Path

```
User action
  └─ ParmRow._dec / _inc            → QSlider.setValue(v ± 1)   ← single step
  └─ ParmRow._on_slider_released    → _send_value(v, mode="absolute")
  └─ ParmRow._on_slider_value       → _send_value(v)  [only when not dragging]
  └─ ParmRow._on_spin_value         → QSlider.setValue(v) → _send_value(v)
       └─ send_mirage_parameter(port, command_id, value,
                                previous_value=_last_sent_value,
                                mode="delta"|"absolute", kind, echo_port)
```

- `mode="delta"` (default for single steps): `shared/sysex.py` walks from `previous_value` to `value` using UP/DOWN arrow key SysEx.
- `mode="absolute"` (slider release): walks from `_last_sent_value` to the released position — covers the full drag range in one paced sequence.
- **Slider drags** suppress per-step sends (`_slider_drag_active = True`) and commit only on release. This prevents flooding the Mirage with intermediate positions.

## Sync / Drift

`_last_sent_value` tracks the last value sent by **this app**. It starts at `spec.min_value`. If the Mirage value diverges (front-panel edit, reboot), the delta walk will start from the wrong baseline.

**Re-sync procedure:** drag the slider to `min_value` and back up to the real Mirage value. After that, `_last_sent_value` matches hardware.

## Panel Colours (QSS)

Colours are applied in `MainWindow._apply_card_style()` via `setStyleSheet`.

| Panel | Border / title | Inner grid lines |
|-------|---------------|-----------------|
| Red | `#b71c1c` / `#8b0000` | `#b71c1c` |
| Yellow | `#d4a017` / `#8a6d00` | `#d4a017` |
| Default | `palette(mid)` | `#888888` |

Object names that drive QSS selectors: `RedParameterCard`, `YellowParameterCard`, `YellowWavesampleProgramCard`, `ParameterCard`.

## Common Tasks

### Add a parameter to an existing card
1. Open `parameter_cards.json`, find the card by `"id"`.
2. Append a new entry to `"params"` (or the appropriate section's `"params"`).
3. Restart the app — no Python changes needed.

### Add a new card
1. Add a JSON object with a unique `"id"` (card ID string) to `parameter_cards.json`.
2. In `main.py`, add the card ID string to one of the panel row tuples (or leave it out for default placement below the panels).
3. If it needs multi-column layout, add its ID → column count to `_REFERENCE_CARD_COLUMN_COUNTS` in `widgets.py`.

### Change a parameter's SysEx kind
Add `"sysex": "wavesample"` or `"sysex": "program"` to the JSON entry. The default is inferred from the card ID containing `"wavesample"`.

### Debug a slider that sends the wrong value
1. Set `MIRAGE_SYSEX_LOG = True` in `shared/config.py` (or `$env:MIRAGE_SYSEX_LOG="1"`).
2. Move the slider and watch the console — it prints `{label} 0x{id:02X} = {value}` per send.
3. Check `_last_sent_value` drift: if the first send goes the wrong direction, the UI's baseline is out of sync with hardware.

## See Also

- [.github/skills/mirage-sysex/SKILL.md](../mirage-sysex/SKILL.md) — SysEx protocol, MASOS, command-code encoding, pacing
- [mirage_parm/docs/README.md](../../../../mirage_parm/docs/README.md) — user-facing docs
- [shared/sysex.py](../../../../shared/sysex.py) — delta/absolute walk implementation
