import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QMenuBar, QVBoxLayout, QWidget, QPushButton
)
from PyQt6.QtGui import QAction


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Диагностика системы")
        self.setGeometry(100, 100, 800, 600)

        # Главное содержимое окна
        self.main_label = QLabel("Добро пожаловать в диагностическую систему!", self)
        self.main_label.setGeometry(50, 50, 700, 30)

        # Создание верхнего меню
        self.menu_bar = self.menuBar()

        # Меню "Редактирование"
        edit_menu = self.menu_bar.addMenu("Редактирование")
        edit_action1 = QAction("Test1", self)
        edit_action2 = QAction("Test2", self)
        edit_action3 = QAction("Test3", self)
        edit_menu.addAction(edit_action1)
        edit_menu.addAction(edit_action2)
        edit_menu.addAction(edit_action3)

        # Меню "Настройка"
        settings_menu = self.menu_bar.addMenu("Настройка")
        settings_action1 = QAction("Test1", self)
        settings_action2 = QAction("Test2", self)
        settings_action3 = QAction("Test3", self)
        settings_menu.addAction(settings_action1)
        settings_menu.addAction(settings_action2)
        settings_menu.addAction(settings_action3)

        # Меню "О приложении"
        about_menu = self.menu_bar.addMenu("О приложении")
        about_action = QAction("О приложении", self)
        about_action.triggered.connect(self.show_about)
        about_menu.addAction(about_action)

        # Кнопка перехода на новый экран
        self.transition_button = QPushButton("Перейти на следующий экран", self)
        self.transition_button.setGeometry(50, 100, 300, 40)
        self.transition_button.clicked.connect(self.open_new_screen)

    def show_about(self):
        """Отобразить окно 'О приложении'."""
        self.main_label.setText("Это приложение для диагностики системы.\nРазработано для дипломного проекта.")
        self.main_label.adjustSize()

    def open_new_screen(self):
        """Переход на новый экран."""
        self.new_screen = SecondScreen(self)
        self.setCentralWidget(self.new_screen)

    def return_to_main_screen(self):
        """Вернуться на главный экран."""
        self.setCentralWidget(None)  # Удаляем текущий виджет
        self.main_label.show()
        self.transition_button.show()


class SecondScreen(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        layout = QVBoxLayout()

        label = QLabel("Это второй экран приложения", self)
        layout.addWidget(label)

        back_button = QPushButton("Вернуться на главный экран", self)
        back_button.clicked.connect(self.return_to_main_screen)
        layout.addWidget(back_button)

        self.setLayout(layout)

    def return_to_main_screen(self):
        """Возврат на главный экран через главное окно."""
        self.main_window.return_to_main_screen()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
