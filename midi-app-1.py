import time
import rtmidi
import os

midiout = rtmidi.MidiOut()
available_ports = midiout.get_ports()

print(available_ports)

if available_ports:
    midiout.open_port(0)
else:
    midiout.open_virtual_port("My virtual output")

with midiout:
    note_c = [0x90, 60, 127] # channel 1, middle C, velocity 112
    note_d = [0x90, 62, 60]
    note_e = [0x90, 64, 30]

    note_off_c = [0x80, 60, 127]
    note_off_d = [0x80, 62, 60]
    note_off_e = [0x80, 64, 30]

    # Send "Note On" messages for all three notes
    midiout.send_message(note_c)
    midiout.send_message(note_d)
    midiout.send_message(note_e)r
    
    # Wait for 1 second
    time.sleep(1.0)
    
    # Send "Note Off" messages for all three notes
    midiout.send_message(note_off_c)
    time.sleep(0.5)
    midiout.send_message(note_off_d)
    midiout.send_message(note_off_e)
    time.sleep(1.0)

del midiout