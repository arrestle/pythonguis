# Mirage Program Dump Format

Source: Advanced Sampler's Guide §3.4 (MASOS appendix).

## Overview

A full program dump is 625 bytes, encoded as nybble pairs:
- Each data byte is sent as two MIDI bytes: `OOOOLLLL` then `OOOOHHHH`
- Low nybble first, high nybble second, MSB always 0

## Request (PC → Mirage)

```
F0 0F 01 03 F7    # lower keyboard (N=0)
F0 0F 01 13 F7    # upper keyboard (N=1)
```

## Response (Mirage → PC) — §3.2.7

```
F0 0F 01 05 [data] F7    # lower
F0 0F 01 15 [data] F7    # upper
```

## Send to Mirage (PC → Mirage) — §3.1.7

```
F0 0F 01 05 [625 bytes as nybble pairs] F7    # lower
F0 0F 01 15 [625 bytes as nybble pairs] F7    # upper
```

## Block Layout (625 bytes total)

| Offset | Length | Content |
|--------|--------|---------|
| 0 | 1 | Sound revision level |
| 1 | 24 | Wavesample Control Block 1 |
| 25 | 24 | Wavesample Control Block 2 |
| 49 | 24 | Wavesample Control Block 3 |
| 73 | 24 | Wavesample Control Block 4 |
| 97 | 24 | Wavesample Control Block 5 |
| 121 | 24 | Wavesample Control Block 6 |
| 145 | 24 | Wavesample Control Block 7 |
| 169 | 24 | Wavesample Control Block 8 |
| 193 | 32 | Segment List, Wavesample 1 |
| 225 | 32 | Segment List, Wavesample 2 |
| 257 | 32 | Segment List, Wavesample 3 |
| 289 | 32 | Segment List, Wavesample 4 |
| 321 | 32 | Segment List, Wavesample 5 |
| 353 | 32 | Segment List, Wavesample 6 |
| 385 | 32 | Segment List, Wavesample 7 |
| 417 | 32 | Segment List, Wavesample 8 |
| 449 | 32 | Segment List, spare |
| 481 | 36 | Program Parameter Block, Program 1 |
| 517 | 36 | Program Parameter Block, Program 2 |
| 553 | 36 | Program Parameter Block, Program 3 |
| 589 | 36 | Program Parameter Block, Program 4 |

**WARNING**: Do NOT modify Wavesample Control Blocks or Segment Lists externally.
Only modify Program Parameter Blocks.

## Program Parameter Block Layout (36 bytes, repeated × 4)

| Byte offset | Param # | Name | Range |
|-------------|---------|------|-------|
| 0 | [29] | Mono Mode Switch | 0–1 |
| 1 | [31] | LFO Frequency | 0–99 |
| 2 | [32] | LFO Depth | 0–99 |
| 3 | [33] | Osc Detune | 0–99 |
| 4 | [34] | Osc Mix | 0–126 |
| 5 | [35] | Mix Vel Sens. | 0–62 |
| 6 | [36] | Filter Cutoff Freq. | 0–198 |
| 7 | [37] | Resonance | 0–80 |
| 8 | [38] | Filter Kbd Tracking | 0–4 |
| 9 | spare | — | 0 |
| 10 | [27] | Initial Wavesample | 0–7 |
| 11 | [28] | Mix Mode Switch | 0–1 |
| 12 | [40] | Filter Attack | 0–31 |
| 13 | [41] | Filter Peak | 0–31 |
| 14 | [42] | Filter Decay | 0–31 |
| 15 | [43] | Filter Sustain | 0–31 |
| 16 | [44] | Filter Release | 0–31 |
| 17 | [45] | Filter Attack Vel. Sens. | 0–62 |
| 18 | [46] | Filter Peak Vel. Sens. | 0–62 |
| 19 | [47] | Filter Decay Kbd. Scaled | 0–62 |
| 20 | [48] | Filter Sustain Vel. Sens. | 0–62 |
| 21 | [49] | Filter Release Vel. Sens. | 0–62 |
| 22 | [50] | Amplitude Attack | 0–31 |
| 23 | [51] | Amplitude Peak | 0–31 |
| 24 | [52] | Amplitude Decay | 0–31 |
| 25 | [53] | Amplitude Sustain | 0–31 |
| 26 | [54] | Amplitude Release | 0–31 |
| 27 | [55] | Amplitude Attack Vel. Sens. | 0–62 |
| 28 | [56] | Amplitude Peak Vel. Sens. | 0–62 |
| 29 | [57] | Amplitude Decay Kbd. Scaled | 0–62 |
| 30 | [58] | Amplitude Sustain Vel. Sens. | 0–62 |
| 31 | [59] | Amplitude Release Vel. Sens. | 0–62 |
| 32–35 | spare | — | 0 |

## Nybble Encoding/Decoding

```python
def encode_nybbles(data: bytes) -> list[int]:
    """Encode raw bytes to MIDI nybble pairs (low nybble first)."""
    out = []
    for b in data:
        out.append(b & 0x0F)          # OOOOLLLL
        out.append((b >> 4) & 0x0F)   # OOOOHHHH
    return out

def decode_nybbles(nybbles: list[int]) -> bytes:
    """Decode MIDI nybble pairs back to raw bytes."""
    out = []
    for i in range(0, len(nybbles), 2):
        lo = nybbles[i] & 0x0F
        hi = nybbles[i+1] & 0x0F
        out.append(lo | (hi << 4))
    return bytes(out)
```

## Workflow: Patch One Parameter via Dump Round-Trip

```python
import mido, time

PORT = "UMC204HD"
LOWER = 0x03  # program dump request, lower

def request_dump(port):
    port.send(mido.Message("sysex", data=[0x0F, 0x01, LOWER]))

def receive_dump(in_port, timeout=2.0):
    deadline = time.time() + timeout
    while time.time() < deadline:
        msg = in_port.receive(block=False)
        if msg and msg.type == "sysex" and len(msg.data) > 3:
            if msg.data[0] == 0x0F and msg.data[1] == 0x01 and msg.data[2] == 0x05:
                return list(msg.data[3:])  # nybble payload
    return None

# Patch param [40] Filter Attack in program 1 (block offset 481, param byte offset 12)
PROG1_BLOCK_OFFSET = 481
FILTER_ATTACK_BYTE = 12

def patch_param(nybbles: list[int], prog1_param_byte: int, new_value: int) -> list[int]:
    raw = decode_nybbles(nybbles)
    ba = bytearray(raw)
    ba[PROG1_BLOCK_OFFSET + prog1_param_byte] = new_value & 0xFF
    return encode_nybbles(bytes(ba))
```
