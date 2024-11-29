# Ensoniq Mirage Controller Design

## Objectives
The controller will:
- Enable real-time MIDI interaction with the Ensoniq Mirage.
- Allow playback and sequencing of MIDI files for pre-recorded tracks.
- Optionally include tools for MIDI message customization and dynamic performance controls.

---

## Features

### 1. Real-Time MIDI Control
- **Purpose**: To play and tweak Mirage parameters live.
- **Requirements**:
  - Low-latency MIDI communication.
  - Support for sending custom CC (Control Change) messages for tweaking filters, pitch, and modulation.
  - Integration with physical knobs/sliders (if hardware is used).
- **Implementation**:
  - Use `python-rtmidi` for real-time MIDI communication.
  - Create custom mappings for Mirage's CC messages.

### 2. MIDI File Playback
- **Purpose**: To send pre-sequenced MIDI data to the Mirage.
- **Requirements**:
  - Ability to read and send MIDI files.
  - Option to loop or chain multiple MIDI files.
- **Implementation**:
  - Use `Mido` for reading and sending MIDI files.
  - Implement basic transport controls (play, pause, stop).

### 3. Sequencer Integration
- **Purpose**: To enable on-the-fly sequencing or step programming.
- **Requirements**:
  - Record real-time input into MIDI files.
  - Step-based sequencing for creating patterns.
- **Implementation**:
  - Use `midiutil` for MIDI file creation.

### 4. Advanced MIDI Manipulation (Optional)
- **Purpose**: For musicians who want more creative tools.
- **Requirements**:
  - Transpose, quantize, or randomize MIDI notes.
  - Map velocity curves to suit Mirage's response.
- **Implementation**:
  - Integrate `pretty_midi` for advanced MIDI analysis and processing.

### 5. User Interface
- **Purpose**: To make the controller user-friendly.
- **Options**:
  - **Graphical**: Create a GUI using PySide6 or PyQt6.
  - **Command-Line**: Provide text-based commands for lightweight setups.
  - **Hardware**: Map MIDI commands to physical controllers like MIDI keyboards or knobs.
- **Implementation**:
  - GUI: Design simple buttons/sliders for interaction.
  - Hardware: Use `python-rtmidi` for real-time control via MIDI controllers.

---

## Architecture

1. **Input Module**
   - Real-time input from MIDI controllers (via `python-rtmidi`).
   - Pre-recorded MIDI file loading (via `Mido`).

2. **Processing Module**
   - Manipulate MIDI data for creative effects (transpose, randomize).
   - Sequence MIDI events for live playback or file creation.

3. **Output Module**
   - Send processed MIDI data to Mirage (via `python-rtmidi`).
   - Save new MIDI sequences (via `midiutil`).

4. **User Interface Module**
   - CLI for basic commands.
   - Optional GUI for intuitive controls.

---

## Example Workflow
1. **Real-Time Playing**:
   - Connect Mirage to controller via MIDI.
   - Use knobs/sliders or a GUI to send CC messages to adjust sound parameters in real time.

2. **MIDI File Playback**:
   - Load a MIDI file into the controller.
   - Play the file, and the Mirage will output the corresponding sounds.

3. **Step Sequencing**:
   - Create a pattern using the sequencer.
   - Send the sequence to the Mirage for playback or save it as a MIDI file.

4. **Advanced Manipulation**:
   - Load a MIDI file for editing.
   - Apply transposition or quantization.
   - Save the modified file for future use.

---

## Tools and Libraries
| Library                | Use Case                                          |
|------------------------|--------------------------------------------------|
| `python-rtmidi`        | Real-time MIDI communication                     |
| `Mido`                 | MIDI file playback and message creation          |
| `midiutil`             | MIDI file creation and sequencing                |
| `pretty_midi`          | Advanced MIDI processing and analysis            |
| `PySide6` or `PyQt6`   | GUI development for an intuitive user interface  |

---

## Next Steps
1. Set up a Python project with the necessary libraries.
2. Implement real-time MIDI communication as a foundation.
3. Expand functionality for MIDI file playback and sequencing.
4. Optionally develop a GUI for user-friendly operation.

Let me know if you'd like detailed implementation code or further refinements!

