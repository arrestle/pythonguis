import time
import os
import subprocess
import mido
import time
import psutil

# Function to check if timidity is installed
def is_timidity_installed():
    try:
        subprocess.run(["timidity", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except FileNotFoundError:
        return False

def is_timidity_running():
    """
    Check if a TiMidity++ process is already running.
    """
    for process in psutil.process_iter(attrs=['name']):
        #print(f"process {process.info['name']}")
        if process.info['name'] == 'timidity':
            print(f"process found: {process.info}")
            return True
    return False
    
# Function to check if timidity is installed and return midi_out
def get_timidity_midi_out():
    try:
        subprocess.run(["timidity", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError:
        print("TiMidity++ is not installed.")
        return None

    print("TiMidity++ is installed.")
    
    if not is_timidity_running():
        # Ensure TiMidity++ is running in ALSA mode
        os.system("timidity -iA &")
        time.sleep(2)  # Wait for TiMidity++ to start
        print("starting timidity")
    else:
        print("timidity is already running.")

    # Get available MIDI output ports
    available_ports = mido.get_output_names()
    
    # Find the first TiMidity port
    timidity_port = next((port for port in available_ports if "TiMidity" in port), None)

    if not timidity_port:
        return None

    print(f"Using MIDI output port: {timidity_port}")
    return mido.open_output(timidity_port)


# Open the first available MIDI output port
available_ports = mido.get_output_names()
print("Available MIDI Output Ports:", len(available_ports))

# Check if timidity is installed
midi_out=get_timidity_midi_out()

if midi_out == None:
    midi_out = mido.open_output(available_ports[0])
    print(f"Opening first port instead {available_ports[0]}")


# Define MIDI messages for notes
note_c = mido.Message('note_on', channel=0, note=60, velocity=127)  # Channel 1, Middle C, Velocity 127
note_d = mido.Message('note_on', channel=0, note=62, velocity=60)   # D
note_e = mido.Message('note_on', channel=0, note=64, velocity=30)   # E

note_off_c = mido.Message('note_off', channel=0, note=60, velocity=127)
note_off_d = mido.Message('note_off', channel=0, note=62, velocity=127)
note_off_e = mido.Message('note_off', channel=0, note=64, velocity=127)

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
