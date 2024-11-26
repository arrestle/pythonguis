## [PythonGUIs](https://www.pythonguis.com) Want to create GUI applications with Python? 
* app-1.py represents [Creating your first app with PySide6](https://www.pythonguis.com/tutorials/pyside6-creating-your-first-window/)
* app-2.py represents [PySide6 Signals, Slots & Events](https://www.pythonguis.com/tutorials/pyside6-signals-slots-events/) Button signals.

* app-3.py represents [PySide6 Signals, Slots & Events](https://www.pythonguis.com/tutorials/pyside6-signals-slots-events/) Connecting widgets together directly.

* app-4.py rerpresents [A Quick Demo: PySide6 Widgets](https://www.pythonguis.com/tutorials/pyside6-widgets/)

* app-5.py rerpresents a Mockup of Sliders for Ensoniq Mirage Controller using a Custom Slider.

* app-6.py Cleaned up version of app-5.py with helper functions.


## Working with [python-rtmidi 1.5.8 ](https://pypi.org/project/python-rtmidi/) from [GitHub](https://github.com/SpotlightKid/python-rtmidi/tree/master) and [Docs](https://spotlightkid.github.io/python-rtmidi/)

Switch to Python 3.12.0 `Press Ctrl + Shift + P and select "Python: Select Interpreter".`

```bash
pyenv install 3.12.0
pyenv global 3.12.0
pyenv rehash
pyenv shell 3.12.0

python -m pip install --upgrade pip
pip install python_rtmidi-1.5.8-cp312-cp312-win_amd64.whl --force-reinstall
```

* midi-app-1.py
* midi-app-2.py
### mido library
* midi-app-3.py

## Mirage Documentation
* Wikipedia explains [Samplers](https://en.wikipedia.org/wiki/Sampler_(musical_instrument))
* [Filter Attack](https://www.manualslib.com/manual/612718/Mirage-Mirage-Dsk-1.html?page=48&term=Filter+Attack&selected=1#manual)
* [Mirage DSK-1 Musicians Manua](https://deepsonic.ch/deep/docs_manuals/ensoniq_mirage_dsk-1_dsk-8_musicians_manual.pdf) see page 49
* [Ensoniq Corporation - Mirage Musician's Manual](http://www.midimanuals.com/manuals/ensoniq/mirage/musicians_manual/) [download](http://www.midimanuals.com/manuals/ensoniq/mirage/musicians_manual/mirage_dsk-1_musicians_manual.pdf)

### MIDI SysEx Structure
* Wikipedia explains [Midi System Exclusive Message](https://en.wikipedia.org/wiki/MIDI#System_Exclusive_messages) which are specific to each manufacturer and model. Original spec [archived](https://web.archive.org/web/20160601121904/https://www.midi.org/specifications).
* Ensoniq manufacturer is `0F` as defined on [MIDI Manufacturer IDs](https://electronicmusic.fandom.com/wiki/List_of_MIDI_Manufacturer_IDs) list.
```
F0 <Manufacturer ID> <Device ID> <Command/Function> <Data Bytes> F7
F0 0E 01 20 7F F7
F0: Start of SysEx.
0E: Manufacturer ID for Ensoniq.
01: Device ID (usually 01 if there's only one device in the chain).
20: Command for a parameter (e.g., filter cutoff).
7F: Data byte representing the parameter value.
F7: End of SysEx.
```
Python
```python
import mido

# Example SysEx message for filter cutoff
sysex_message = [0xF0, 0x0E, 0x01, 0x22, 0x64, 0xF7]  # Adjust filter cutoff to 100
with mido.open_output("Your MIDI Port Name") as midi_out:
    midi_out.send(mido.Message('sysex', data=sysex_message))
```