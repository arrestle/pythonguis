import time
import mido

# Open the first available MIDI output port
available_ports = mido.get_output_names()
print("Available MIDI Output Ports:", available_ports)

if available_ports:
    midi_out = mido.open_output(available_ports[0])
else:
    raise Exception("No available MIDI output ports.")

# Define MIDI messages for notes
note_c = mido.Message('note_on', channel=0, note=60, velocity=127)  # Channel 1, Middle C, Velocity 127
note_d = mido.Message('note_on', channel=0, note=62, velocity=60)   # D
note_e = mido.Message('note_on', channel=0, note=64, velocity=30)   # E

note_off_c = mido.Message('note_off', channel=0, note=60, velocity=127)
note_off_d = mido.Message('note_off', channel=0, note=62, velocity=127)
note_off_e = mido.Message('note_off', channel=0, note=64, velocity=127)

# Send "Note On" messages
with midi_out:
    print("Sending Note On messages...")
    midi_out.send(note_c)
    time.sleep(0.5)
    midi_out.send(note_d)
    time.sleep(0.5)
    midi_out.send(note_e)

    # Wait for 1 second
    time.sleep(1.0)

    # Send "Note Off" messages
    print("Sending Note Off messages...")
    midi_out.send(note_off_c)
    time.sleep(0.5)
    midi_out.send(note_off_d)
    midi_out.send(note_off_e)
    time.sleep(1.0)
