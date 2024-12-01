from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout, QWidget, QGroupBox, QHBoxLayout, QLabel, QPushButton, QSlider
from ensoniq.config import MANUFACTURER_ID, DEVICE_ID, MIDI_PORT_NAME
import mido


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
        self.group_box = QGroupBox(f"{title} (0x{midi_sysex_command_id:02X})")
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
        self.group_box.setLayout(group_box_layout)

        # Add group box to main layout
        layout.addWidget(self.group_box)
        self.setLayout(layout)

    def get_tick_interval(self, max_value):
        if max_value <= 10:
            return 1
        elif max_value <= 32:
            return 5
        return 10

    def update_value(self, value):
        self.value_label.setText(str(value))


        print(f"Slider {self.sysex_command_id:02X} {self.title} value changed to {value}")
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
            sysex_data = [MANUFACTURER_ID, DEVICE_ID, self.sysex_command_id, value]
            self.midi_port.send(mido.Message('sysex', data=sysex_data))
            sysex_message_hex = ' '.join(f'{byte:02X}' for byte in sysex_data)
            print(f"Sent SysEx message in hex: F0 {sysex_message_hex} F7")
