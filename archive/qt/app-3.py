import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction


from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QLineEdit,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QMenu,
    QPushButton,
)

class CustomBlock(QPushButton):
    def mousePressEvent(self, e):
        print("CustomBlock mousePressEvent")
        e.accept() # accept the event, stopping it from propagating

class CustomPropagate(QPushButton):
    def mousePressEvent(self, e):
        print("CustomPropagate mousePressEvent")
        e.ignore() # propagate the event to parent

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("My App")

        self.label1 = QLabel()
        # make the label light blue and italic
        self.label1.setStyleSheet("color: #0000ff; font-style: italic")

        self.lineEdit = QLineEdit()

        # connect the textChanged signal to the setText slot
        self.lineEdit.textChanged.connect(self.label1.setText) 

        layout = QVBoxLayout()
        layout.addWidget(self.lineEdit)
        layout.addWidget(self.label1)

        self.label = QLabel("Click in this box, right-click for context menu")
        self.label.setStyleSheet("background-color: yellow")
        layout.addWidget(self.label)

        self.button1 = CustomBlock("Ignore Me!")
        layout.addWidget(self.button1)

        self.button2 = CustomPropagate("Propagate Me!")
        layout.addWidget(self.button2)

        container = QWidget()
        container.setLayout(layout)

        self.setCentralWidget(container)


    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            # handle the left-button press in here
            self.label.setText("mousePressEvent LEFT")

        elif e.button() == Qt.MouseButton.MiddleButton:
            # handle the middle-button press in here.
            self.label.setText("mousePressEvent MIDDLE")

        elif e.button() == Qt.MouseButton.RightButton:
            # handle the right-button press in here.
            self.label.setText("mousePressEvent RIGHT")

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self.label.setText("mouseReleaseEvent LEFT")

        elif e.button() == Qt.MouseButton.MiddleButton:
            self.label.setText("mouseReleaseEvent MIDDLE")

        elif e.button() == Qt.MouseButton.RightButton:
            self.label.setText("mouseReleaseEvent RIGHT")

    def mouseDoubleClickEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self.label.setText("mouseDoubleClickEvent LEFT")

        elif e.button() == Qt.MouseButton.MiddleButton:
            self.label.setText("mouseDoubleClickEvent MIDDLE")

        elif e.button() == Qt.MouseButton.RightButton:
            self.label.setText("mouseDoubleClickEvent RIGHT")

    def contextMenuEvent(self, e):
        context = QMenu(self)
        context.addAction(QAction("test 1", self))
        context.addAction(QAction("test 2", self))
        context.addAction(QAction("test 3", self))

        action4 = QAction("test 4", self)
        # make action4 special
        action4.triggered.connect(lambda: self.label.setText("test 4 selected"))
        context.addAction(action4)

        context.exec(e.globalPos())

    def mousePressEvent(self, event):
        print("Mouse pressed!")
        super().mousePressEvent(event)

app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()