"""Original Mirage main window and entrypoint."""

import sys

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QMenuBar,
    QMenu,
    QVBoxLayout,
    QWidget,
    QHBoxLayout,
)

from mirage_orig.mirage_slider import MirageSlider
from shared.config import MIDI_PORT_NAME, TITLE
from shared.midi import open_midi_output_port


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(TITLE)

        self.midi_port, self.midi_port_name = open_midi_output_port(MIDI_PORT_NAME)

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

        main_layout.addLayout(
            self.create_column_of_sliders(
                [
                    ("Filter Kbd Tracker", 10, 0x40),
                    ("Relative Filter Freq", 99, 0x15),
                    ("Max Filter Freq", 99, 0x16),
                    ("Filter Attack", 31, 0x17),
                    ("Filter Peak", 31, 0x18),
                    ("Filter Decay", 31, 0x19),
                    ("Filter Sustain", 31, 0x1A),
                ]
            )
        )

        main_layout.addLayout(
            self.create_column_of_sliders(
                [
                    ("Filter Release", 31, 0x1B),
                    ("Filter Cutoff", 99, 0x1C),
                    ("Filter Attack Vel", 31, 0x1D),
                    ("Filter Peak Vel", 31, 0x1E),
                    ("Filter Decay Scaled", 31, 0x1F),
                    ("Filter Sustain Vel", 31, 0x20),
                    ("Filter Release Vel", 31, 0x21),
                ]
            )
        )

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


class MirageMain:
    """Small helper used by tests; not required for the GUI entrypoint."""

    def __init__(self, midi_port):
        self.midi_port = midi_port
        self.slider = MirageSlider(midi_port, 100, "Test Slider", 0x42)

    def start(self):
        if self.slider:
            self.slider.show()

    def stop(self):
        if self.slider:
            self.slider.hide()


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
