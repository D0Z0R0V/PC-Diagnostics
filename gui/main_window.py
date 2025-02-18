from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QWidget, QStackedWidget, QListWidget, QGridLayout, QListWidgetItem, QMenu
)
from PyQt6.QtGui import QPixmap, QAction, QIcon
from PyQt6.QtCore import Qt
from PyQt6.QtCore import QSize
from PyQt6.QtCore import QTimer

from core.cpu import get_cpu_info
from core.gpu import monitor_gpu
from core.ram import monitor_ram
from core.hdd import monitor_hdd


import sys, json


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Диагностика системы")
        self.setGeometry(100, 100, 1200, 800)

        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)

        self.menu_list = QListWidget()
        self.menu_list.setMaximumWidth(200)
        self.menu_list.itemClicked.connect(self.switch_screen)
        self.init_menu_list()
        main_layout.addWidget(self.menu_list)

        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)
        self.init_screens()

        self.setCentralWidget(main_widget)
        self.create_menus()

    def init_menu_list(self):
        """Инициализация левого меню с иконками."""
        menu_items = [
            ("Общие сведения", "gui/img/general.png"),
            ("Процессор", "gui/img/cpu.png"),
            ("Оперативная память", "gui/img/ram.png"),
            ("Дисковая подсистема", "gui/img/disk.png"),
            ("Видеокарта", "gui/img/gpu.png"),
            ("Материнская плата", "gui/img/motherboard.png"),
            ("Напряжение", "gui/img/volt.png"),
            ("Диагностика", "gui/img/diag.png"),
            ("Тестирование", "gui/img/test.png"),
        ]

        for text, icon_path in menu_items:
            item = QListWidgetItem()
            item.setText(text)
            item.setIcon(QIcon(icon_path))
            self.menu_list.addItem(item)

    def create_menus(self):
        """Создаем верхнее меню приложения."""
        menu_bar = self.menuBar()

        # Файл
        file_menu = menu_bar.addMenu("Файл")
        file_menu.addAction(QAction("Text 1", self))
        file_menu.addAction(QAction("Text 2", self))

        # Настройки
        settings_menu = menu_bar.addMenu("Настройки")
        settings_menu.addAction(QAction("Text 3", self))
        settings_menu.addAction(QAction("Text 4", self))

        # Отчет
        report_menu = menu_bar.addMenu("Отчет")
        report_menu.addAction(QAction("Text 5", self))

        # Помощь
        help_menu = menu_bar.addMenu("Помощь")
        help_menu.addAction(QAction("Text 6", self))
        help_menu.addAction(QAction("Text 7", self))

        # О приложении
        about_menu = menu_bar.addMenu("О приложении")
        about_action = QAction("О программе", self)
        about_action.triggered.connect(self.show_about)
        about_menu.addAction(about_action)

    def init_screens(self):
        """Инициализация экранов для QStackedWidget."""
        self.general_info_screen = self.create_general_screen()
        self.processor_screen = self.CPU_info_screen("Процессор", "Информация о процессоре.", "gui/img/cpu.png")
        self.memory_screen = self.RAM_info_screen("Оперативная память", "Информация о памяти.", "gui/img/ram.png")
        self.disk_screen = self.HDD_info_screen("Дисковая подсистема", "Информация о дисках.", "gui/img/disk.png")
        self.gpu_screen = self.GPU_info_screen("Видеокарта", "Информация о видеокарте.", "gui/img/gpu.png")
        self.motherboard_screen = self.create_info_screen("Материнская плата", "Информация о материнской плате.", "gui/img/motherboard.png")
        self.voltage_screen = self.create_info_screen("Напряжение", "Информация о напряжении.", "gui/img/volt.png")
        self.diagnostic_screen = self.create_info_screen("Диагностика", "Режим диагностики системы.", "gui/img/diag.png")
        self.testing_screen = self.create_info_screen("Тестирование", "Тестирование системы на устойчивость.", "gui/img/test.png")
        
        self.stacked_widget.addWidget(self.general_info_screen)
        self.stacked_widget.addWidget(self.processor_screen)
        self.stacked_widget.addWidget(self.memory_screen)
        self.stacked_widget.addWidget(self.disk_screen)
        self.stacked_widget.addWidget(self.gpu_screen)
        self.stacked_widget.addWidget(self.motherboard_screen)
        self.stacked_widget.addWidget(self.voltage_screen)
        self.stacked_widget.addWidget(self.diagnostic_screen)
        self.stacked_widget.addWidget(self.testing_screen)
        self.stacked_widget.setCurrentWidget(self.general_info_screen)

    def create_general_screen(self):
        """Создаем экран 'Общие сведения' с сеткой карточек."""
        screen = QWidget()
        layout = QGridLayout(screen)

        cards = [
            ("Процессор", "gui/img/cpu.png"),
            ("Оперативная память", "gui/img/ram.png"),
            ("Дисковая подсистема", "gui/img/disk.png"),
            ("Видеокарта", "gui/img/gpu.png"),
            ("Материнская плата", "gui/img/motherboard.png"),
            ("Напряжение", "gui/img/volt.png"),
            ("Диагностика", "gui/img/diag.png"),
            ("Тестирование", "gui/img/test.png"),
        ]

        for i, (title, icon_path) in enumerate(cards):
            card = QPushButton()
            card.setText(title)
            card.setStyleSheet("text-align: center;")
            if icon_path:
                card.setIcon(QIcon(icon_path))
                card.setIconSize(QSize(80, 80))
            card.clicked.connect(lambda _, t=title: self.switch_screen_by_title(t))
            layout.addWidget(card, i // 4, i % 4)

        return screen
    
    def CPU_info_screen(self, title, description, image_path=None):
        screen = QWidget()
        layout = QVBoxLayout(screen)

        image_label = QLabel(self)
        pixmap = QPixmap("gui/img/cpu.png")
        image_label.setPixmap(pixmap.scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio))
        layout.addWidget(image_label, alignment=Qt.AlignmentFlag.AlignCenter)

        title_label = QLabel("<h1>Процессор</h1>", self)
        layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.cpu_info_label = QLabel("Загрузка: --%", self)
        layout.addWidget(self.cpu_info_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Запуск таймера для обновления
        self.cpu_timer = QTimer()
        self.cpu_timer.timeout.connect(self.update_cpu_info)
        self.cpu_timer.start(500)  # обновление каждые 0.5 секунды

        return screen

    def update_cpu_info(self):
        """Обновление информации о процессоре."""
        cpu_data = get_cpu_info()  # Получаем словарь

        if "error" in cpu_data:
            cpu_text = f"Ошибка: {cpu_data['error']}"
        else:
            cpu_text = (
                f"Загрузка: {cpu_data['usage']}%\n"
                f"Ядер: {cpu_data['cores']}\n"
                f"Потоков: {cpu_data['threads']}\n"
                f"Частота: {cpu_data['freq_current']} MHz (мин {cpu_data['freq_min']}, макс {cpu_data['freq_max']})\n"
            )

            # Добавляем температуру, если есть
            if cpu_data["temperatures"]:
                temp_texts = []
                for sensor, entries in cpu_data["temperatures"].items():
                    for entry in entries:
                        temp_texts.append(
                            f"{entry['label']}: {entry['current']}°C (макс {entry['high']}, крит {entry['critical']})"
                        )
                cpu_text += "\nТемпературы:\n" + "\n".join(temp_texts)

        self.cpu_info_label.setText(cpu_text)
        
    def GPU_info_screen(self, title, description, image_path=None):
        screen = QWidget()
        layout = QVBoxLayout(screen)

        # Изображение GPU
        image_label = QLabel(self)
        pixmap = QPixmap("gui/img/gpu.png")
        image_label.setPixmap(pixmap.scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio))
        layout.addWidget(image_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Заголовок
        title_label = QLabel("<h1>Видеокарта</h1>", self)
        layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Виджет для информации о видеокарте
        self.gpu_info_label = QLabel("Загрузка: --%", self)
        layout.addWidget(self.gpu_info_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Таймер для обновления данных
        self.gpu_timer = QTimer()
        self.gpu_timer.timeout.connect(self.update_gpu_info)
        self.gpu_timer.start(500)  # Обновление каждую секунду

        return screen
    
    def update_gpu_info(self):
        gpu_data_list = monitor_gpu()

        if not gpu_data_list:
            self.gpu_info_label.setText("Ошибка: Не удалось получить данные о видеокарте")
            return

        # Формируем текст для всех видеокарт
        gpu_text = ""
        for i, gpu_data in enumerate(gpu_data_list):
            gpu_text += (
                f"<b>GPU {i}: {gpu_data['gpu']}</b>\n"
                f"Загрузка: {gpu_data['load']}%\n"
                f"Загрузка памяти: {gpu_data['ram_load']}%\n"
                f"Температура: {gpu_data['temperature']}°C\n"
                f"Частота чипа: {gpu_data['chip']} МГц\n\n"
            )

        self.gpu_info_label.setText(gpu_text)
        
    def RAM_info_screen(self, title, description, image_path=None):
        screen = QWidget()
        layout = QVBoxLayout(screen)
        
        image_label = QLabel(self)
        pixmap = QPixmap("gui/img/ram.png")
        image_label.setPixmap(pixmap.scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio))
        layout.addWidget(image_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        title_text = QLabel("<h1>Оперативная память</h1>", self)
        layout.addWidget(title_text, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.ram_info_label = QLabel("Загрузка: --%", self)
        layout.addWidget(self.ram_info_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.ram_timer = QTimer()
        self.ram_timer.timeout.connect(self.update_ram_info)
        self.ram_timer.start(500)
        
        return screen
    
    def update_ram_info(self):
        ram_info = monitor_ram()
        
        if not ram_info:
            self.ram_info_label.setText("Ошибка: Не удалось получить данные о RAM")
            return
        else:
            ram_text = (
                f"Общий объем памяти: {ram_info['ram']} ГБ\n"
                f"Свободное место: {ram_info['free']} ГБ\n"
                f"Используется сейчас: {ram_info['usage']} ГБ\n"
                f"Занято: {ram_info['percent']} %"
            )
            
        self.ram_info_label.setText(ram_text)
        
    def HDD_info_screen(self, title, description, image_path=None):
        screen = QWidget()
        layout = QVBoxLayout(screen)
        
        image_label = QLabel(self)
        pixmap = QPixmap("gui/img/disk.png")
        image_label.setPixmap(pixmap.scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio))
        layout.addWidget(image_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        title_lable = QLabel("<h1>Диск</h1>", self)
        layout.addWidget(title_lable, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.hdd_info_label = QLabel("Загрузка: --%", self)
        layout.addWidget(self.hdd_info_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.hdd_time = QTimer()
        self.hdd_time.timeout.connect(self.update_hdd_info)
        self.hdd_time.start(500)
        
        return screen
    
    def update_hdd_info(self):
        hdd_info = monitor_hdd()
        
        if not hdd_info:
            self.hdd_info_label.setText("Ошибка: Не удалось получить данные о диске(HDD)")
            
        else:
            hdd_text = (
                f"Процентр использования: {hdd_info['percent']}%\n"
                f"Точка подключения: {hdd_info['device']}\n"
                f"Тип системы: {hdd_info['file_sys']}\n"
                f"Объем диска: {hdd_info['size']} \n"
                f"Использовано памяти: {hdd_info['used']}\n"
                f"Свободно памяти: {hdd_info['free']}\n")
            
        self.hdd_info_label.setText(hdd_text)
            
        
    def create_info_screen(self, title, description, image_path=None):
        """Создаем экран с информацией"""
        screen = QWidget()
        main_layout = QHBoxLayout(screen)
        
        # Левая часть с изображением
        left_layout = QVBoxLayout()
        if image_path:
            image_label = QLabel(self)
            pixmap = QPixmap(image_path)
            if pixmap.isNull():
                print(f"Ошибка: не удалось загрузить изображение по пути: {image_path}")
                return screen
            resized_pixmap = pixmap.scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            image_label.setPixmap(resized_pixmap)
            left_layout.addWidget(image_label, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        
        left_layout.addStretch()  
        
        # Правая часть с текстом
        right_layout = QVBoxLayout()
        title_label = QLabel(f"<h1>{title}</h1>", self)
        right_layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        description_label = QLabel(description, self)
        right_layout.addWidget(description_label, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        
        right_layout.addStretch()  

        
        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)

        return screen

    def switch_screen(self, item):
        """Переключение экранов по выбору в боковом меню."""
        screens = {
            "Общие сведения": self.general_info_screen,
            "Процессор": self.processor_screen,
            "Оперативная память": self.memory_screen,
            "Дисковая подсистема": self.disk_screen,
            "Видеокарта": self.gpu_screen,
            "Материнская плата": self.motherboard_screen,
            "Напряжение": self.voltage_screen,
            "Диагностика": self.diagnostic_screen,
            "Тестирование": self.testing_screen
        }
        selected_screen = screens.get(item.text())
        if selected_screen:
            self.stacked_widget.setCurrentWidget(selected_screen)

    def switch_screen_by_title(self, title):
        """Переключение экранов по нажатию на карточку."""
        screens = {
            "Общие сведения": self.general_info_screen,
            "Процессор": self.processor_screen,
            "Оперативная память": self.memory_screen,
            "Дисковая подсистема": self.disk_screen,
            "Видеокарта": self.gpu_screen,
            "Материнская плата": self.motherboard_screen,
            "Напряжение": self.voltage_screen,
            "Диагностика": self.diagnostic_screen,
            "Тестирование": self.testing_screen
        }
        selected_screen = screens.get(title)
        if selected_screen:
            self.stacked_widget.setCurrentWidget(selected_screen)

    def show_about(self):
        """Отображение информации 'О приложении'."""
        about_text = "Это приложение для диагностики системы.\nРазработано для дипломного проекта."
        self.general_info_screen.layout().itemAt(1).widget().setText(about_text)
        self.stacked_widget.setCurrentWidget(self.general_info_screen)



