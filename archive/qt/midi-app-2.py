import rtmidi

def send_sysex_message(midi_out, sysex_data):
    """
    Sends a SysEx message via the provided MIDI output port.
    
    Parameters:
        midi_out (rtmidi.MidiOut): The MIDI output port.
        sysex_data (list of int): The SysEx message as a list of bytes.
    """
    # Send the SysEx message
    midi_out.send_message(sysex_data)
    
    # Print the message in hexadecimal format
    hex_message = " ".join(f"{byte:02X}" for byte in sysex_data)
    print(f"Sent SysEx message: {hex_message}")

# Initialize MIDI output
midi_out = rtmidi.MidiOut()
available_ports = midi_out.get_ports()

# Open the first available MIDI port
if available_ports:
    midi_out.open_port(0)
else:
    midi_out.open_virtual_port("Virtual MIDI Output")

# Example SysEx message for a fictional device
# Start of SysEx: 0xF0
# Manufacturer ID: 0x7E (Educational/Non-Commercial)
# Device ID: 0x10
# Command: Set parameter 0x20 to value 0x40
# End of SysEx: 0xF7
sysex_message = [0xF0, 0x7E, 0x10, 0x20, 0x40, 0xF7]

# Send the SysEx message
send_sysex_message(midi_out, sysex_message)

# Close the MIDI output
midi_out.close_port()
