import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QMenuBar, QMenu, QVBoxLayout, QWidget, QGroupBox, QHBoxLayout, QLabel, QPushButton, QSlider
import mido

# Create a constant for midi interface
MANUFACTURER_ID = 0x0F
DEVICE_ID = 0x01
MIDI_PORT_NAME = 'Microsoft GS Wavetable Synth 0' #tbd needs to be ensoniq


class MirageSlider(QWidget):
    def __init__(self, midi_port, max_value, title, midi_sysex_command_id, parent=None):
        super().__init__(parent)

        self.midi_port = midi_port  # MIDI output port
        self.title = title
        self.sysex_command_id = midi_sysex_command_id  # MIDI Control Change number
        self.midi_channel = 0  # Default MIDI channel (0-based, corresponds to channel 1)
        self.midi_out = None  # MIDI output port to send messages

        # Main layout for the slider group
        layout = QVBoxLayout()

        # Group box for the slider
        group_box = QGroupBox(title)
        group_box_layout = QVBoxLayout()

        # Horizontal layout for min and max labels
        labels_layout = QHBoxLayout()
        self.min_label = QLabel("0")
        self.min_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        labels_layout.addWidget(self.min_label)
        labels_layout.addStretch()
        self.max_label = QLabel(str(max_value))
        self.max_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        labels_layout.addWidget(self.max_label)
        group_box_layout.addLayout(labels_layout)

        # Slider with buttons
        slider_layout = QHBoxLayout()

        # Decrement button
        decrement_button = QPushButton("<")
        decrement_button.setFixedSize(20, 20)
        decrement_button.clicked.connect(self.decrease_value)
        slider_layout.addWidget(decrement_button)

        # Slider
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, max_value)
        self.slider.setValue(0)
        self.slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.slider.setTickInterval(self.get_tick_interval(max_value))
        self.slider.valueChanged.connect(self.update_value)
        slider_layout.addWidget(self.slider)

        # Increment button
        increment_button = QPushButton(">")
        increment_button.setFixedSize(20, 20)
        increment_button.clicked.connect(self.increase_value)
        slider_layout.addWidget(increment_button)

        # Add slider layout and value label to group box
        group_box_layout.addLayout(slider_layout)
        self.value_label = QLabel("0")
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        group_box_layout.addWidget(self.value_label)
        group_box.setLayout(group_box_layout)

        # Add group box to main layout
        layout.addWidget(group_box)
        self.setLayout(layout)

    def get_tick_interval(self, max_value):
        if max_value <= 10:
            return 1
        elif max_value <= 32:
            return 5
        return 10

    def update_value(self, value):
        self.value_label.setText(str(value))
        print(f"Slider {self.title} value changed to {value}")
        self.send_midi_message(value)

    def decrease_value(self):
        current_value = self.slider.value()
        if current_value > self.slider.minimum():
            self.slider.setValue(current_value - 1)

    def increase_value(self):
        current_value = self.slider.value()
        if current_value < self.slider.maximum():
            self.slider.setValue(current_value + 1)

    def send_midi_message(self, value):
        if self.midi_port:
            # Create and send a MIDI CC message
            sysex_data = [MANUFACTURER_ID, DEVICE_ID, self.sysex_command_id, self.slider.value()]
            self.midi_port.send(mido.Message('sysex', data=sysex_data))
            sysex_message_hex = ' '.join(f'{byte:02X}' for byte in sysex_data)
            print(f"Sent SysEx message in hex: F0 {sysex_message_hex} F7")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Ensoniq Mirage Controller with MIDI")

        available_ports = mido.get_output_names()
        print("Available MIDI Output Ports:", available_ports)

        if available_ports:
            self.midi_port = mido.open_output(available_ports[0])
        else:
            raise Exception("No available MIDI output ports.")

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

        # Add two columns with sliders
        main_layout.addLayout(self.create_column_of_sliders([
            ("Filter Kbd Tracker", 10, 38),
            ("Relative Filter Freq", 99, 21),
            ("Max Filter Freq", 99, 22),
            ("Filter Attack", 31, 23),
            ("Filter Peak", 31, 24),
            ("Filter Decay", 31, 25),
            ("Filter Sustain", 31, 26),
        ]))

        main_layout.addLayout(self.create_column_of_sliders([
            ("Filter Release", 31, 27),
            ("Filter Cutoff", 99, 28),
            ("Filter Attack Vel", 31, 29),
            ("Filter Peak Vel", 31, 30),
            ("Filter Decay Scaled", 31, 31),
            ("Filter Sustain Vel", 31, 32),
            ("Filter Release Vel", 31, 33),
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


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()
