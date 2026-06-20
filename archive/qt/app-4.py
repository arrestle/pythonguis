import sys
from PySide6.QtCore import Qt

from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDateTimeEdit,
    QDial,
    QDoubleSpinBox,
    QFontComboBox,
    QLabel,
    QLCDNumber,
    QLineEdit,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QSlider,
    QSpinBox,
    QTimeEdit,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
)


import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QSlider, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QWidget
)

class CustomSlider(QWidget):
    def __init__(self, max_value, title, parent=None):
        super().__init__(parent)
        
        # Main vertical layout
        main_layout = QVBoxLayout()
        
        # Title label
        self.title_label = QLabel(title)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.title_label)

        # Horizontal layout for labels and slider
        labels_layout = QHBoxLayout()
        
        # Minimum value label
        self.min_label = QLabel("0")
        self.min_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        labels_layout.addWidget(self.min_label)
        
        # Spacer for the slider
        labels_layout.addStretch()
        
        # Maximum value label
        self.max_label = QLabel(str(max_value))
        self.max_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        labels_layout.addWidget(self.max_label)
        
        main_layout.addLayout(labels_layout)
        
        # Horizontal layout for slider and buttons
        slider_layout = QHBoxLayout()
        
        # Decrement button
        self.decrement_button = QPushButton("◀")
        self.decrement_button.clicked.connect(self.decrease_value)
        self.decrement_button.setFixedSize(20, 20)
        slider_layout.addWidget(self.decrement_button)
        
        # Slider
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, max_value)
        self.slider.setValue(0)  # Initial value
                # Add ticks to the slider
        self.slider.setTickPosition(QSlider.TickPosition.TicksBelow)

        if max_value <= 10:
            self.slider.setTickInterval(1)
        elif max_value <= 32:
            self.slider.setTickInterval(5)
        else:
            self.slider.setTickInterval(10)

        self.slider.valueChanged.connect(self.update_value_label)  # Connect value change
        slider_layout.addWidget(self.slider)
        
        # Increment button
        self.increment_button = QPushButton("▶")
        self.increment_button.clicked.connect(self.increase_value)
        self.increment_button.setFixedSize(20, 20)
        slider_layout.addWidget(self.increment_button)
        
        main_layout.addLayout(slider_layout)
        
        # Value label
        self.value_label = QLabel("0")
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.value_label)
                # Horizontal layout for labels and slider
        labels_layout = QHBoxLayout()
        
        # Minimum value label
        self.min_label = QLabel("0")
        self.min_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        labels_layout.addWidget(self.min_label)
        
        # Spacer for the slider
        labels_layout.addStretch()
        
        # Maximum value label
        self.max_label = QLabel(str(max_value))
        self.max_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        labels_layout.addWidget(self.max_label)
        
        # main_layout.addLayout(labels_layout)
        self.setLayout(main_layout)

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

        layout = QVBoxLayout()
        widgets = [
            QCheckBox,
            QComboBox,
            QDateEdit,
            QDateTimeEdit,
            QDial,
            QDoubleSpinBox,
            QFontComboBox,
            QLCDNumber,
            QLabel,
            QLineEdit,
            QProgressBar,
            QPushButton,
            QRadioButton,
            QSlider,
            QSpinBox,
            QTimeEdit,
        ]

        # for widget in widgets:
        #     layout.addWidget(widget())

        slider = [CustomSlider(10, "Filter Kbd Tracker"), 
                  CustomSlider(99, "Relative Filter Freq"), 
                  CustomSlider(99, "Max Filter Freq"), 
                  CustomSlider(31, "Filter Attack")]
        
        for s in slider:
            layout.addWidget(s)

        central_widget = QWidget()
        central_widget.setLayout(layout)

        self.setCentralWidget(central_widget)

app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()