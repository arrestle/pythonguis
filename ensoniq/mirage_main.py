import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PySide6.QtWidgets import QApplication, QMainWindow, QMenuBar, QMenu, QVBoxLayout, QWidget, QHBoxLayout, QGroupBox, QLabel
import mido
from ensoniq.mirage_slider import MirageSlider
from ensoniq.config import MANUFACTURER_ID, DEVICE_ID, MIDI_PORT_NAME, TITLE


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(TITLE)

        available_ports = mido.get_output_names()
        print("Available MIDI Output Ports:", available_ports)

        # find port matching the MIDI_PORT_NAME
        for port in available_ports:
            if MIDI_PORT_NAME in port:
                self.midi_port = mido.open_output(port)
                self.midi_port_name = port
                break
        else:
            raise Exception(f"No available MIDI output port matching '{MIDI_PORT_NAME}'.")

        # if available_ports:
        #     self.midi_port = mido.open_output(available_ports[0])
        # else:
        #     raise Exception("No available MIDI output ports.")

        # Central widget and layout
        central_widget = QWidget()

        menu_bar = QMenuBar(self)
        self.setMenuBar(menu_bar)

        view_menu = QMenu("View", self)
        menu_bar.addMenu(view_menu)

        param_menu = QMenu("Param", self)
        menu_bar.addMenu(param_menu)

        wave_menu = QMenu("Wave", self)
        menu_bar.addMenu(wave_menu)

        main_layout = QHBoxLayout()

        # Add first columns with sliders
        main_layout.addLayout(self.create_column_of_sliders([
            ("Filter Kbd Tracker", 10, 0x40),
            ("Relative Filter Freq", 99, 0x15),
            ("Max Filter Freq", 99, 0x16),
            ("Filter Attack", 31, 0x17),
            ("Filter Peak", 31, 0x18),
            ("Filter Decay", 31, 0x19),
            ("Filter Sustain", 31, 0x1A),
        ]))

        # Add second column with sliders
        main_layout.addLayout(self.create_column_of_sliders([
            ("Filter Release", 31, 0x1B),
            ("Filter Cutoff", 99, 0x1C),
            ("Filter Attack Vel", 31, 0x1D),
            ("Filter Peak Vel", 31, 0x1E),
            ("Filter Decay Scaled", 31, 0x1F),
            ("Filter Sustain Vel", 31, 0x20),
            ("Filter Release Vel", 31, 0x21),
        ]))

        # Set the layout
        central_widget.setLayout(main_layout)
        central_widget.setMinimumWidth(800)
        self.setCentralWidget(central_widget)

    def create_column_of_sliders(self, sliders):
        """Helper function to create a column of sliders."""
        column_layout = QVBoxLayout()
        column_layout.setSpacing(0)
        column_layout.setContentsMargins(0, 0, 0, 0)
        for title, max_value, midi_cc in sliders:
            slider = MirageSlider(self.midi_port, max_value, title, midi_cc)
            column_layout.addWidget(slider)
        return column_layout

# Move application startup to a function
def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

class MirageMain:
    def __init__(self, midi_port):
        self.midi_port = midi_port
        self.slider = MirageSlider(midi_port, 100, "Test Slider", 0x42)

    def start(self):
        if self.slider:
            self.slider.show()

    def stop(self):
        if self.slider:
            self.slider.hide()

class MirageSlider(QWidget):
    def __init__(self, midi_port, max_value, title, midi_sysex_command_id, parent=None):
        super().__init__(parent)
        self.midi_port = midi_port
        self.max_value = max_value
        self.title = title
        self.midi_sysex_command_id = midi_sysex_command_id
        self.group_box = QGroupBox()
        layout = QHBoxLayout()
        layout.addWidget(QLabel(title))
        layout.addStretch()
        layout.addWidget(QLabel(f"0x{midi_sysex_command_id:02X}"))
        self.group_box.setLayout(layout)
        # ...existing code...
