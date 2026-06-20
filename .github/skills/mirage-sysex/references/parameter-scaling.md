# Mirage Parameter Display vs Wire Value Scaling

Source: Advanced Sampler's Guide §3.5.1 — parameters marked `*` are displayed ÷ 2.

When using §3.1.1 command-code SysEx to set values, digits sent are the **display** value (what the front panel shows). The Mirage handles the internal conversion.

When reading §3.2.1/3.2.2 transmit packets, the wire value is the **internal** value — divide by 2 for display-scaled parameters.

## Scaling Table

| Param # | Name | Display Range | Internal Range | Scale |
|---------|------|--------------|----------------|-------|
| [21] | Master Tune | 0–99 | 0–99 | 1:1 |
| [22] | Pitch Bender Range | 0–17 | 0–34 | display × 2 |
| [23] | Keyboard Vel. Sens. | 0–31 | 0–63 | display × 2 |
| [24] | Keyboard Balance | 0–63 | 0–126 | display × 2 |
| [25] | U/L Program Link | 0–40 | 0–40 | 1:1 |
| [26] | Wavesample Select | 1–8 | 0–7 | display − 1 |
| [27] | Initial Wavesample | 1–8 | 0–7 | display − 1 |
| [28] | Mix Mode | On/Off | 0–1 | toggle |
| [29] | Monophonic Mode | On/Off | 0–1 | toggle |
| [31] | LFO Freq (Speed) | 0–99 | 0–99 | 1:1 |
| [32] | LFO Depth | 0–99 | 0–99 | 1:1 |
| [33] | Osc 2 Detune | 0–99 | 0–99 | 1:1 |
| [34] | Osc Mix | 0–63 | 0–126 | display × 2 |
| [35] | Osc Mix Vel. Sens. | 0–31 | 0–62 | display × 2 |
| [36] | Filter Cutoff Freq | 0–99 | 0–198 | display × 2 |
| [37] | Filter Resonance (Q) | 0–40 | 0–80 | display × 2 |
| [38] | Filter Kbd. Tracking | 0–4 | 0–4 | 1:1 |
| [40] | Filter Envelope — Attack | 0–31 | 0–31 | 1:1 |
| [41] | Filter Envelope — Peak | 0–31 | 0–31 | 1:1 |
| [42] | Filter Envelope — Decay | 0–31 | 0–31 | 1:1 |
| [43] | Filter Envelope — Sustain | 0–31 | 0–31 | 1:1 |
| [44] | Filter Envelope — Release | 0–31 | 0–31 | 1:1 |
| [45–49] | Filter Envelope Mod (vel/kbd) | 0–31 | 0–62 | display × 2 |
| [50] | Amplitude Envelope — Attack | 0–31 | 0–31 | 1:1 |
| [51] | Amplitude Envelope — Peak | 0–31 | 0–31 | 1:1 |
| [52] | Amplitude Envelope — Decay | 0–31 | 0–31 | 1:1 |
| [53] | Amplitude Envelope — Sustain | 0–31 | 0–31 | 1:1 |
| [54] | Amplitude Envelope — Release | 0–31 | 0–31 | 1:1 |
| [55–59] | Amplitude Envelope Mod | 0–31 | 0–62 | display × 2 |
| [60] | Wavesample Start | 00–FE (hex) | 0–254 | hex display |
| [61] | Wavesample End | 01–FF (hex) | 1–255 | hex display |
| [62] | Loop Start | 00–FE (hex) | 0–254 | hex display |
| [63] | Loop End | 01–FF (hex) | 1–255 | hex display |
| [64] | Loop End Fine Adj. | 00–FF (hex) | 0–255 | hex display |
| [65] | Loop Switch | On/Off | 0–1 | toggle |
| [66] | Wavesample Rotate | 00–FF (hex) | 0–255 | hex display |
| [67] | Relative Tuning — Coarse | 0–7 | 0–7 | 1:1 |
| [68] | Relative Tuning — Fine | 0–255 | 0–255 | 1:1 |
| [69] | Relative Amplitude | 0–63 | 0–63 | 1:1 |
| [70] | Relative Filter Freq. | 0–99 | 0–198 | display × 2 |
| [71] | Maximum Filter Freq. | 0–99 | 0–198 | display × 2 |
| [72] | Top Key | 1–61 | 0–60 | display − 1 |
| [73] | Sample Time Adj. | 20–99 | 20–99 | 1:1 |
| [74] | Input Filter Freq. | 0–99 | 0–198 | display × 2 |
| [75] | Line/Mic Level Input | On/Off | 0–1 | toggle |
| [76] | Sampling Threshold | 0–63 | 0–126 | display × 2 |
| [77] | User Multisampling | On/Off | 0–1 | toggle |
| [81] | MIDI Omni Mode | On/Off | 0–1 | toggle |
| [82] | MIDI Channel Select | 1–16 | 0–15 | display − 1 |
| [83] | MIDI Thru Mode | On/Off | 0–1 | toggle |
| [84] | MIDI Controller Enable | On/Off | 0–1 | toggle |
| [85] | Ext. Sequencer Clock | On/Off | 0–1 | toggle |
| [86] | Ext. Clock Jack Select | On/Off | 0–1 | toggle |
| [87] | Internal Clock Rate | 0–99 | 0–99 | 1:1 |
| [88] | Sequencer Loop Switch | On/Off | 0–1 | toggle |
| [89] | Seq. Ft. Sw./Sus. Pedal | On/Off | 0–1 | toggle |
| [91] | External Computer Switch | On/Off | 0–1 | toggle (must be ON) |
| [92] | Baud Rate Switch | On/Off | 0–1 | toggle |
| [93] | Cartridge Filter Freq. | 0–25 | 0–25 | 1:1 |

## Notes

- Scaling is inferred from the dump table in §3.4/§3.5 of the Advanced Sampler's Guide combined
  with observed wire values captured from MIDI-OX front-panel monitoring.
- Envelope modulation params [45–49] and [55–59] marked `*` in §3.5.1 — "displayed divided by 2".
- When in doubt, capture the front-panel transmit packet with MIDI-OX and decode the wire value.
