import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("My App")
        self.button_is_checked = False

        button = QPushButton("Press Me!")
        button.setCheckable(True)
        button.clicked.connect(self.the_button_was_clicked)
        button.clicked.connect(self.the_button_was_toggled)
        button.released.connect(self.the_button_was_released)

        # Set the central widget of the Window.
        self.setCentralWidget(button)
        self.button = button # so that self.button.isChecked() can be called

    def the_button_was_clicked(self):
        print("Clicked!")
    def the_button_was_toggled(self, checked):
        self.button_is_checked = checked
        print("Checked?", self.button_is_checked)
        self.button.setEnabled(False)
        self.setWindowTitle("Button disabled")

    def the_button_was_released(self):
        self.button_is_checked = self.button.isChecked()
        print("Released?", self.button_is_checked)


app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()