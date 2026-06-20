MANUFACTURER_ID = 0x0F
DEVICE_ID = 0x01
# Substring of a mido output name (see mirage_parm docs). Must match exactly one port.
# Examples: "Microsoft GS Wavetable" (soft synth), "UMC204HD" (interface to Mirage).
MIDI_PORT_NAME = "UMC204HD"
# Optional second output: duplicate SysEx here (e.g. loopMIDI port name) so MIDI-OX can monitor.
MIDI_ECHO_PORT_NAME = ""
TITLE = "Ensoniq Mirage Controller with MIDI"

# SysEx §3.2.1 / §3.2.2 (Advanced Samplers Guide): program vs wavesample parameter messages.
MIRAGE_UPPER_KEYBOARD = False  # False = lower keyboard (N=0 in docs)
MIRAGE_PROGRAM_SELECT = 0  # 0–3 (four programs per side)
MIRAGE_WAVESAMPLE_SELECT = 0  # 0–7; used for 0x0E wavesample-parameter messages

# Default Mirage parameter index for docs / smoke tests (card: GENERAL KEYBOARD — MASTER TUNE).
MIRAGE_DEFAULT_PARAMETER_NUMBER = 21

# Log every parameter SysEx to stderr as hex (F0 … F7). Env MIRAGE_SYSEX_LOG=1 also enables.
MIRAGE_SYSEX_LOG = True
