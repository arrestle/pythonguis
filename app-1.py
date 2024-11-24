import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget



# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Andrea")
        self.setFixedSize(400, 200)
        central_widget = QWidget(self)
        central_widget.setMinimumSize(400, 200)
        central_widget.setStyleSheet("background-color: lightblue")
        self.setCentralWidget(central_widget)

        # Create a layout for the central widget
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        button = QPushButton("Press Me!")
        # add clickCount attribute to the button
        button.clickCount = 0
    
        #make the button background color light green hover color dark green
        button.setStyleSheet("""
            QPushButton {
                background-color: lightgreen;
                border: 1px solid darkgreen;
                color: black;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: darkgreen;
                color: white;
            }""")

        label = QLabel("Hello World")
        #make the label background color light pink add a padding of 10px
        label.setStyleSheet("""
            QLabel {
                background-color: pink;
                padding: 10px;
                border: 1px solid red;
            }
            QLabel:hover {
                background-color: red;
                color: white;
            }""")
        central_widget.setMouseTracking(True)

        layout.addWidget(button)
        layout.addWidget(label)

        # Set the central widget of the Window.
        central_widget.setLayout(layout)

        # add the label below the button
        # self.addDockWidget(Qt.BottomDockWidgetArea, label)

        # when button is clicked, set the label text to "Button Clicked n times"
        button.clicked.connect(lambda: self.buttonClicked(button, label))

    def buttonClicked(self, button, label):
        button.clickCount += 1
        label.setText(f"Label Button Clicked {button.clickCount} times")


app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()