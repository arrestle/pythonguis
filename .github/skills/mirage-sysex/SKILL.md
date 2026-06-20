---
name: mirage-sysex
description: 'Ensoniq Mirage MIDI SysEx protocol knowledge for this project. Use when: debugging parameter changes not reaching the Mirage, adding new parameters, changing value encoding, investigating why sliders have no effect, understanding MASOS vs standard OS differences, working on shared/sysex.py, mirage_parm/widgets.py, or shared/config.py.'
argument-hint: 'Describe the SysEx or parameter issue'
---

# Ensoniq Mirage SysEx — Project Knowledge

## Key Files

| File | Role |
|------|------|
| [shared/sysex.py](../../../../shared/sysex.py) | All SysEx send logic — edit here first |
| [shared/config.py](../../../../shared/config.py) | MIDI port, device ID, upper/lower, program, wavesample |
| [mirage_parm/parameter_cards.json](../../../../mirage_parm/parameter_cards.json) | Parameter IDs, display ranges, labels |
| [mirage_parm/parameters.py](../../../../mirage_parm/parameters.py) | JSON → ParmSpec dataclass; sysex_kind per card |
| [mirage_parm/widgets.py](../../../../mirage_parm/widgets.py) | Slider/spinbox → send_mirage_parameter() |

## MASOS vs Standard OS

The Mirage boots from a disk. Two OS variants matter:

| OS | Boots from | SysEx receive support |
|----|-----------|----------------------|
| Standard OS | Sound disk or blank formatted disk | Notes only; no parameter-set receive command |
| **MASOS** | MASOS disk (included with Advanced Sampler's Guide) | Full SysEx control including §3.1.1 command codes |

**This project targets MASOS.** If the Mirage is not responding to SysEx at all, first confirm it booted from the MASOS disk.

## Protocol Reference (MASOS MIDI Implementation)

Source: `Mirage-docs/mirage_advanced_samplers_guide.txt` (OCR of original manual).

### SysEx Header (all messages)

```
F0  0F  01  <msg-type>  <payload>  F7
    ^   ^
    |   Mirage device code (always 0x01)
    Ensoniq manufacturer ID
```

In mido, omit F0/F7 — they are added automatically:
```python
mido.Message("sysex", data=[0x0F, 0x01, <msg-type>, ...])
```

---

### §3.1 — Receive Data (PC → Mirage)

#### §3.1.1 Front-Panel Command Code (the ONLY way to set individual parameters)

```
F0 0F 01  01  [keypad bytes, max 5]  7F  F7
              ^                      ^
              message type           end-of-command marker
```

Keypad byte codes (Table 3.3):

| Key | Hex | Notes |
|-----|-----|-------|
| 0–9 | 0x00–0x09 | digit keys |
| PARAM | 0x0C | enters parameter-select mode |
| VALUE | 0x0D | enters value-display/edit mode |
| ENTER | 0x0E | confirms; also UP ARROW in value mode |
| CANCEL | 0x0F | cancels; also DOWN ARROW in value mode |

**Confirmed working sequence** (two SysEx messages, split to stay within 5-byte limit):

```python
# Select parameter 36 (Filter Cutoff), enter value mode
msg1 = [0x0F, 0x01, 0x01,  0x0C, 0x03, 0x06, 0x0D, 0x09, 0x02]  # PARAM 3 6 VALUE 9 2 — no ENTER, 5 payload bytes

# Confirm
msg2 = [0x0F, 0x01, 0x01,  0x0E, 0x7F]  # ENTER
```

**Important constraints discovered through testing:**
- Maximum 5 keypad bytes per SysEx message.
- Messages exceeding 5 keypad bytes are silently ignored.
- State may or may not be preserved between messages — test before relying on it.
- Sending VALUE + digits as a standalone second message causes parameter selection, not value entry.

#### §3.1.2 Program Dump Request

```
F0 0F 01  03  F7         (lower keyboard, N=0)
F0 0F 01  13  F7         (upper keyboard, N=1)
```

Mirage responds with §3.2.7 Program Dump Data (625 bytes encoded as nybbles).

#### §3.1.7 Program Dump Data (send all program parameters at once)

```
F0 0F 01  05  [625 bytes encoded as nybble pairs]  F7   (lower, N=0)
F0 0F 01  15  [...]  F7                                 (upper, N=1)
```

See [references/program-dump-format.md](./references/program-dump-format.md) for byte offsets.

---

### §3.2 — Transmit Data (Mirage → PC — READ ONLY, do not send these)

#### §3.2.1 Program Parameter Message

```
F0 0F 01  0D  <scope>  <param#>  <val-LS>  <val-MS>  F7
```

- `scope` = `OOONOOPP`: N=upper/lower (bit 4), PP=program 0–3 (bits 0–1)
- `param#` = parameter number (decimal, same as card id)
- Value encoded as two nybble bytes, LS first: value = `val-LS | (val-MS << 4)`

**This is TRANSMIT ONLY.** The Mirage sends this when you edit a parameter on the front panel.
Sending 0x0D inbound is silently ignored.

#### §3.2.2 Wavesample Parameter Message

```
F0 0F 01  0E  <scope>  <param#>  <val-LS>  <val-MS>  F7
```

- `scope` = `OOONOSSS`: N=upper/lower (bit 4), SSS=wavesample 0–7 (bits 0–2)

Also TRANSMIT ONLY.

---

## Value Encoding

### Nybble encoding (used in §3.2 transmit messages only)

```python
ls = value & 0x0F          # low nybble → first byte (OOOOVVVV)
ms = (value >> 4) & 0x0F   # high nybble → second byte
# Reassemble: value = ls | (ms << 4)
```

Example: captured packet `F0 0F 01 0D 00 24 0C 05 F7`
- param = 0x24 = 36 (Filter Cutoff)
- ls = 0x0C, ms = 0x05 → value = 0x0C | (0x05 << 4) = 0x5C = 92
- Display shows 46 because this parameter's display = internal ÷ 2

### Display-vs-wire scaling

Some parameters have display ranges that differ from internal wire values:

| Parameter | Display range | Wire range | Conversion |
|-----------|--------------|------------|------------|
| [36] Filter Cutoff Freq | 0–99 | 0–198 | wire = display × 2 |
| [37] Filter Resonance (Q) | 0–40 | 0–80 | wire = display × 2 |
| [70] Relative Filter Freq | 0–99 | 0–198 | wire = display × 2 |
| [71] Maximum Filter Freq | 0–99 | 0–198 | wire = display × 2 |
| All envelope params [40–59] | 0–31 | 0–31 | 1:1 |
| [69] Relative Amplitude | 0–63 | 0–63 | 1:1 |

Full scaling table is in [references/parameter-scaling.md](./references/parameter-scaling.md).

---

## Diagnostic Checklist

When parameter changes have no effect on Mirage:

1. **Boot disk**: Is Mirage running MASOS? (Required for SysEx parameter control.)
2. **MIDI routing**: PC MIDI OUT → Mirage MIDI IN. Notes working ≠ SysEx working.
3. **Parameter [91]**: External Computer Switch must be ON. Front panel: PARAM 9 1 ENTER → value must be 1.
4. **Enable SysEx logging**: Set `MIRAGE_SYSEX_LOG = True` in [shared/config.py](../../../../shared/config.py) or `$env:MIRAGE_SYSEX_LOG="1"`.
5. **Replay test**: Capture a front-panel edit with MIDI-OX, then replay the exact bytes from Python.
6. **5-byte limit**: Command-code SysEx accepts at most 5 keypad bytes per message. Longer sequences are silently ignored.
7. **Value scaling**: For §3.1.1 command codes, digits typed are the DISPLAY value. For some params (Filter Cutoff etc.) the display value ≠ internal value — use the scaling table.

---

## Quick Reference: Replay Test (mido one-liner)

```powershell
# Activate this repo's venv first: .\.venv\Scripts\Activate.ps1
# Replay exact captured SysEx (replace bytes as needed):
python -c "import mido; p=next(x for x in mido.get_output_names() if 'UMC204HD' in x); o=mido.open_output(p); o.send(mido.Message('sysex', data=[0x0F,0x01,0x0D,0x00,0x24,0x0C,0x05])); o.close(); print('sent')"
```

## See Also

- [references/program-dump-format.md](./references/program-dump-format.md) — full 625-byte program block layout
- [references/parameter-scaling.md](./references/parameter-scaling.md) — display vs wire value for every parameter
- `Mirage-docs/mirage_advanced_samplers_guide.txt` — OCR source (MASOS appendix starts ~line 3720)
- `Mirage-docs/mirage-parameter-cards.extracted.txt` — parameter card labels and ranges
