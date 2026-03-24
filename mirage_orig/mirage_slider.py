from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QVBoxLayout,
    QWidget,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QGridLayout,
)
import sys
import mido
import threading
import time
import traceback

from shared.sysex import send_mirage_parameter


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

        play_btn = QPushButton("Play Sound")
        # QPushButton.clicked emits (bool checked); slot must accept it or use lambda.
        play_btn.clicked.connect(self._on_play_sound_clicked)
        layout.addWidget(play_btn)

        # Align tick buttons once layout is established
        QTimer.singleShot(100, self.align_tick_buttons)

    def _on_play_sound_clicked(self, checked: bool = False) -> None:
        """Play short test notes (GM-friendly); `checked` comes from QPushButton.clicked."""
        # Run off the Qt GUI thread: long sleeps on the main thread can upset some
        # Windows MIDI drivers / scheduling; GS Wavetable still uses your default speakers.
        threading.Thread(target=self._play_test_tones_worker, daemon=True).start()

    def play_test_tones(self):
        """Same as Play Sound button; kept for tests / direct calls (runs in current thread)."""
        self._play_test_tones_worker()

    def _play_test_tones_worker(self) -> None:
        """Send GM program change + short C-major arp on MIDI channel 1 (index 0)."""
        print(f"Play Sound: {self.title} (slider 0x{self.sysex_command_id:02X})")

        ch = 0  # MIDI channel 1
        note1, note2, note3 = 60, 64, 67  # C4, E4, G4

        try:
            # Select Acoustic Grand (GM prog 0). GS Wavetable often stays silent without this.
            self.midi_port.send(mido.Message("program_change", channel=ch, program=0))
            time.sleep(0.05)

            note_on = [
                mido.Message("note_on", channel=ch, note=note1, velocity=120),
                mido.Message("note_on", channel=ch, note=note2, velocity=100),
                mido.Message("note_on", channel=ch, note=note3, velocity=100),
            ]
            note_off = [
                mido.Message("note_off", channel=ch, note=note1, velocity=64),
                mido.Message("note_off", channel=ch, note=note2, velocity=64),
                mido.Message("note_off", channel=ch, note=note3, velocity=64),
            ]

            print("Play Sound: sending Note On…")
            self.midi_port.send(note_on[0])
            time.sleep(0.2)
            self.midi_port.send(note_on[1])
            time.sleep(0.2)
            self.midi_port.send(note_on[2])
            time.sleep(0.5)
            print("Play Sound: sending Note Off…")
            for msg in note_off:
                self.midi_port.send(msg)
            print("Play Sound: done.")
        except Exception:
            print("Play Sound: MIDI send failed:", file=sys.stderr)
            traceback.print_exc()

    def get_tick_interval(self, max_value):
        if max_value <= 10:
            return 1
        elif max_value <= 32:
            return 5
        return 10

    def update_value(self, value):
        self.value_label.setText(str(value))
        print(f"Slider {self.title} {self.sysex_command_id:02X} {value}")
        # Mirage parameters are SysEx, not control change. GS Wavetable etc. will
        # ignore these; use a real Mirage (or MIDI monitor) to verify.
        self.send_midi_message(value)

    def add_tick_buttons(self):
        """Add buttons for tick marks."""
        self.tick_buttons = []
        tick_interval = self.get_tick_interval(self.max_value)
        num_ticks = self.max_value // tick_interval + 1

        for i in range(num_ticks):
            tick_value = i * tick_interval
            button = QPushButton(str(tick_value))
            button.setFixedSize(20, 15)
            button.clicked.connect(lambda _, val=tick_value: self.set_slider_value(val))

            button.setStyleSheet(
                """
                        border: none;
                        font-size: 10px;
                    """
            )

            self.tick_buttons.append((button, tick_value))
            self.tick_buttons_layout.addWidget(button, 0, i)

    def align_tick_buttons(self):
        """Align buttons with tick marks after slider geometry is available."""
        if not self.slider.width():
            return

        tick_interval = self.get_tick_interval(self.max_value)
        slider_width = self.slider.width()

        for button, tick_value in self.tick_buttons:
            proportion = tick_value / self.max_value
            button_x = int(proportion * slider_width) - button.width() // 2
            button.move(
                self.slider.geometry().x() + button_x,
                self.slider.geometry().bottom() + 10,
            )

    def set_slider_value(self, value):
        """Sets the slider value and triggers the valueChanged event."""
        if isinstance(value, str):
            value = int(value)
        self.slider.setValue(value)

    def decrease_value(self):
        """Decrease the slider value by one step."""
        current_value = self.slider.value()
        if current_value > self.slider.minimum():
            self.slider.setValue(current_value - 1)

    def increase_value(self):
        """Increase the slider value by one step."""
        current_value = self.slider.value()
        if current_value < self.slider.maximum():
            self.slider.setValue(current_value + 1)

    def send_midi_message(self, value):
        if self.midi_port:
            send_mirage_parameter(self.midi_port, self.sysex_command_id, value)
