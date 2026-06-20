import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QSlider, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QGroupBox, QWidget
)

class MirageSlider(QWidget):
    def __init__(self, max_value, title, parent=None):
        super().__init__(parent)
        
        # Main vertical layout
        main_layout = QVBoxLayout()
        
        # Group box for the slider and controls
        group_box = QGroupBox(title)
        group_box_layout = QVBoxLayout()
        
        # Horizontal layout for labels (min and max values)
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
        
        group_box_layout.addLayout(labels_layout)
        
        # Horizontal layout for slider and buttons
        slider_layout = QHBoxLayout()
        
        # Decrement button
        self.decrement_button = QPushButton("<")
        self.decrement_button.setFixedSize(20, 20)  # Small fixed size for the button
        self.decrement_button.clicked.connect(self.decrease_value)
        slider_layout.addWidget(self.decrement_button)
        
        # Slider
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, max_value)
        self.slider.setValue(0)  # Initial value
        self.slider.valueChanged.connect(self.update_value_label)  # Connect value change
        
        # Add ticks to the slider
        self.slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        if max_value <= 10:
            self.slider.setTickInterval(1)
        elif max_value <= 32:
            self.slider.setTickInterval(5)
        else:
            self.slider.setTickInterval(10)
        slider_layout.addWidget(self.slider)
        
        # Increment button
        self.increment_button = QPushButton(">")
        self.increment_button.setFixedSize(20, 20)  # Small fixed size for the button
        self.increment_button.clicked.connect(self.increase_value)
        slider_layout.addWidget(self.increment_button)
        
        group_box_layout.addLayout(slider_layout)
        
        # Value label
        self.value_label = QLabel("0")
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        group_box_layout.addWidget(self.value_label)
        
        # Set the layout for the group box
        group_box.setLayout(group_box_layout)
        
        # Add the group box to the main layout
        main_layout.addWidget(group_box)
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

                # Group box for the slider and controls
        group_box = QGroupBox("columns")
        group_box_layout = QHBoxLayout()

        column1_layout = QVBoxLayout()
        #set the minimum horizontal size of the layout
        column1_layout.setSpacing(0)
        column1_layout.setContentsMargins(0, 0, 0, 0)

        column1_sliders = [MirageSlider(10, "Filter Kbd Tracker"), 
                  MirageSlider(99, "Relative Filter Freq"), 
                  MirageSlider(99, "Max Filter Freq"), 
                  MirageSlider(31, "Filter Attack"),
                  MirageSlider(31, "Filter Peak"),
                  MirageSlider(31, "Filter Decay"),
                  MirageSlider(31, "Filter Sustain"),]
        
        for s in column1_sliders:
            column1_layout.addWidget(s)

        group_box_layout.addLayout(column1_layout)

        column2_layout = QVBoxLayout()
        #set the minimum horizontal size of the layout
        column2_layout.setSpacing(0)
        column2_layout.setContentsMargins(0, 0, 0, 0)

        column2_sliders = [MirageSlider(31, "Filter Release"), 
                  MirageSlider(99, "Filter Cutoff"), 
                  MirageSlider(31, "Filter Attack Vel"), 
                  MirageSlider(31, "Filter Peak Vel"), 
                  MirageSlider(31, "Filter Decay Scaled"),
                  MirageSlider(31, "Filter Sustain Vel"),
                  MirageSlider(31, "Filter Release Vel"),]
        
        for s in column2_sliders:
            column2_layout.addWidget(s)

        central_widget = QWidget()

        # Add the layouts to the central widget
        group_box_layout.addLayout(column2_layout)
        group_box.setLayout(group_box_layout)

        central_widget.setLayout(group_box_layout)
        central_widget.setMinimumWidth(800)

        self.setCentralWidget(central_widget)

app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()