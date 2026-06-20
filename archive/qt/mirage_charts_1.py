# Define a dictionary to store SysEx message details
sys_ex_messages = {
    "Filter Frequency": {
        "command_id": 0x22,
        "description": "Adjusts the filter cutoff frequency.",
        "value_range": (0, 127),
    },
    "Filter Resonance": {
        "command_id": 0x23,
        "description": "Adjusts the filter resonance.",
        "value_range": (0, 127),
    },
    "Envelope Sustain": {
        "command_id": 0x25,
        "description": "Sets the envelope sustain level.",
        "value_range": (0, 127),
    },
    "LFO Rate": {
        "command_id": 0x30,
        "description": "Adjusts the LFO rate.",
        "value_range": (0, 127),
    },
    # Add additional parameters from the document as needed
}

# Example function to send a SysEx message
import mido

def send_sysex_message(parameter_name, value, midi_port_name):
    """
    Sends a SysEx message to the Mirage for the given parameter and value.

    Args:
        parameter_name (str): The name of the parameter (e.g., "Filter Frequency").
        value (int): The value to set for the parameter (0-127).
        midi_port_name (str): The name of the MIDI output port.
    """
    if parameter_name not in sys_ex_messages:
        print(f"Error: Parameter '{parameter_name}' not found.")
        return

    # Get the command ID and construct the SysEx message
    parameter = sys_ex_messages[parameter_name]
    command_id = parameter["command_id"]

    # Validate the value range
    min_value, max_value = parameter["value_range"]
    if not (min_value <= value <= max_value):
        print(f"Error: Value {value} out of range for {parameter_name} ({min_value}-{max_value}).")
        return

    # Construct the SysEx message
    sysex_message = [0xF0, 0x0E, 0x01, command_id, value, 0xF7]

    # Send the SysEx message via mido
    with mido.open_output(midi_port_name) as midi_out:
        midi_out.send(mido.Message('sysex', data=sysex_message))
        print(f"Sent SysEx message for {parameter_name}: {sysex_message}")

# Example usage
if __name__ == "__main__":
    midi_port_name = "Your MIDI Port Name"  # Replace with the correct MIDI port name
    send_sysex_message("Filter Frequency", 100, midi_port_name)
