import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QLineEdit, QVBoxLayout, QWidget
from PyQt6.QtCore import QSize
from random import choice

window_titles = [
    'My App',
    'My App',
    'Still My App',
    'Still My App',
    'What on earth',
    'What on earth',
    'This is surprising',
    'This is surprising',
    'Something went wrong'
]

class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        
        self.button_is_chacked = True

        self.setWindowTitle("My App")
        self.setMinimumSize(QSize(600, 500))
        
        self.button = QPushButton("Жми!")
        self.button.setCheckable(True)
        self.button.clicked.connect(self.the_button_was_clicked)
        self.button.released.connect(self.the_button_was_released)
        self.windowTitleChanged.connect(self.the_window_was_changed)
        
        self.setCentralWidget(self.button)
        
    def the_button_was_released(self):
        self.button_is_chacked = self.button.isChecked()
        
        print(self.button_is_chacked)
        
    def the_button_was_clicked(self):
        print("Clicked")
        new_window_title = choice(window_titles)
        print("Setting title: %s" % new_window_title)
        self.setWindowTitle(new_window_title)
        
    def the_window_was_changed(self, window_title):
        print("Window title changed: %s" % window_title)
        
        if window_title == "Something went wrong":
            self.button.setDisabled(True)


app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()