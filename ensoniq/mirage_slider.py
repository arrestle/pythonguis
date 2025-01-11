from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QVBoxLayout, QWidget, QGroupBox, QHBoxLayout, QLabel, QPushButton, QSlider, QGridLayout
import mido, time

class MirageSlider(QWidget):
    def __init__(self, midi_port, max_value, title, midi_sysex_command_id, parent=None):
        super().__init__(parent)

        self.midi_port = midi_port
        self.title = title
        self.sysex_command_id = midi_sysex_command_id
        self.midi_channel = 0
        self.max_value = max_value

        # Main layout for the slider group
        layout = QVBoxLayout()

        # Group box for the slider
        self.group_box = QGroupBox(f"{title}  0x{midi_sysex_command_id:02X}  ")
        group_box_layout = QVBoxLayout()

        # Horizontal layout for min, value, and max labels
        labels_layout = QHBoxLayout()
        self.min_label = QLabel("0")
        self.min_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        labels_layout.addWidget(self.min_label)

        self.value_label = QLabel("0")
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        labels_layout.addWidget(self.value_label)

        self.max_label = QLabel(str(max_value))
        self.max_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        labels_layout.addWidget(self.max_label)

        group_box_layout.addLayout(labels_layout)

        # Slider with increment and decrement buttons
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

        # Add slider layout to the group box
        group_box_layout.addLayout(slider_layout)

        # Tick buttons
        self.tick_buttons_layout = QGridLayout()
        self.add_tick_buttons()
        group_box_layout.addLayout(self.tick_buttons_layout)

        self.group_box.setLayout(group_box_layout)
        layout.addWidget(self.group_box)
        self.setLayout(layout)
        
        play_sound = QPushButton("Play Sound")
        play_sound.clicked.connect(self.play_sound)
        layout.addWidget(play_sound)

        # Align tick buttons once layout is established
        QTimer.singleShot(100, self.align_tick_buttons)

    def play_sound(self):
        print(f"Playing sound for {self.title} slider...")
        
        # Define MIDI messages for notes
        note_c = mido.Message('note_on', channel=0, note=60, velocity=127)  # Channel 1, Middle C, Velocity 127
        note_d = mido.Message('note_on', channel=0, note=62, velocity=60)   # D
        note_e = mido.Message('note_on', channel=0, note=64, velocity=30)   # E

        note_off_c = mido.Message('note_off', channel=0, note=60, velocity=127)
        note_off_d = mido.Message('note_off', channel=0, note=62, velocity=127)
        note_off_e = mido.Message('note_off', channel=0, note=64, velocity=127)

        # Send "Note On" messages
        print("Sending Note On messages...")
        self.midi_port.send(note_c)
        time.sleep(0.5)
        self.midi_port.send(note_d)
        time.sleep(0.5)
        self.midi_port.send(note_e)

        # Wait for 1 second
        time.sleep(1.0)

        # Send "Note Off" messages
        print("Sending Note Off messages...")
        self.midi_port.send(note_off_c)
        time.sleep(0.5)
        self.midi_port.send(note_off_d)
        self.midi_port.send(note_off_e)
        time.sleep(1.0)

    def get_tick_interval(self, max_value):
        if max_value <= 10:
            return 1
        elif max_value <= 32:
            return 5
        return 10

    def update_value(self, value):
        self.value_label.setText(str(value))
        print(f"Slider {self.title} {self.sysex_command_id:02X} {value}")
        self.midi_port.send(mido.Message('control_change', channel=self.midi_channel, control=self.sysex_command_id, value=value))
        

    def add_tick_buttons(self):
        """
        Add buttons for tick marks.
        """
        self.tick_buttons = []
        tick_interval = self.get_tick_interval(self.max_value)
        num_ticks = self.max_value // tick_interval + 1

        for i in range(num_ticks):
            tick_value = i * tick_interval
            button = QPushButton(str(tick_value))
            button.setFixedSize(20, 15)  # Adjust size as needed
            button.clicked.connect(lambda _, val=tick_value: self.set_slider_value(val))
            
            # set button border to empty
            button.setStyleSheet("""
                        border: none;
                        font-size: 10px;  /* Smaller text size */
                    """)  # Remove borders and adjust text size as needed   
            
            self.tick_buttons.append((button, tick_value))
            self.tick_buttons_layout.addWidget(button, 0, i)

    def align_tick_buttons(self):
        """
        Align buttons with tick marks after slider geometry is available.
        """
        if not self.slider.width():
            return  # Skip alignment if slider geometry is not ready

        tick_interval = self.get_tick_interval(self.max_value)
        slider_width = self.slider.width()
        num_ticks = len(self.tick_buttons)

        for index, (button, tick_value) in enumerate(self.tick_buttons):
            # Calculate the pixel position of the tick mark
            proportion = tick_value / self.max_value
            button_x = int(proportion * slider_width) - button.width() // 2
            button.move(self.slider.geometry().x() + button_x, self.slider.geometry().bottom() + 10)

    def set_slider_value(self, value):
        """
        Sets the slider value and triggers the valueChanged event.
        """
        if isinstance(value, str):
            value = int(value)
        self.slider.setValue(value)

    def decrease_value(self):
        """
        Decrease the slider value by one step.
        """
        current_value = self.slider.value()
        if current_value > self.slider.minimum():
            self.slider.setValue(current_value - 1)

    def increase_value(self):
        """
        Increase the slider value by one step.
        """
        current_value = self.slider.value()
        if current_value < self.slider.maximum():
            self.slider.setValue(current_value + 1)
