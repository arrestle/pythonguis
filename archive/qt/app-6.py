import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QSlider, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QGroupBox, QWidget
)



class MirageSlider(QWidget):
    def __init__(self, max_value, title, parent=None):
        super().__init__(parent)
        
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
        self.slider.valueChanged.connect(self.update_value_label)
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

    def update_value_label(self, value):
        self.value_label.setText(str(value))

    def decrease_value(self):
        current_value = self.slider.value()
        if current_value > self.slider.minimum():
            self.slider.setValue(current_value - 1)

    def increase_value(self):
        current_value = self.slider.value()
        if current_value < self.slider.maximum():
            self.slider.setValue(current_value + 1)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Ensoniq Mirage Controller")

        # Central widget and layout
        central_widget = QWidget()
        main_layout = QHBoxLayout()

        # Add two columns with sliders
        main_layout.addLayout(self.create_column([
            ("Filter Kbd Tracker", 10),
            ("Relative Filter Freq", 99),
            ("Max Filter Freq", 99),
            ("Filter Attack", 31),
            ("Filter Peak", 31),
            ("Filter Decay", 31),
            ("Filter Sustain", 31),
        ]))

        main_layout.addLayout(self.create_column([
            ("Filter Release", 31),
            ("Filter Cutoff", 99),
            ("Filter Attack Vel", 31),
            ("Filter Peak Vel", 31),
            ("Filter Decay Scaled", 31),
            ("Filter Sustain Vel", 31),
            ("Filter Release Vel", 31),
        ]))

        # Set the layout
        central_widget.setLayout(main_layout)
        central_widget.setMinimumWidth(800)
        self.setCentralWidget(central_widget)

    def create_column(self, sliders):
        """Helper function to create a column of sliders."""
        column_layout = QVBoxLayout()
        column_layout.setSpacing(0)
        column_layout.setContentsMargins(0, 0, 0, 0)
        for title, max_value in sliders:
            column_layout.addWidget(MirageSlider(max_value, title))
        return column_layout


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()
