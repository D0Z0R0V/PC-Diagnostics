from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize, QProcess
from PyQt6.QtWidgets import (
    QApplication, QSizePolicy, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QWidget, QStackedWidget, QListWidget, QGridLayout, QListWidgetItem, QMenu,
    QProgressBar, QMessageBox, QGroupBox, QScrollArea, QFormLayout, QFrame
)
from PyQt6.QtGui import QPixmap, QAction, QIcon

from data.model.model import DiagnosticModel
from core.cpu import get_cpu_info
from core.gpu import monitor_gpu
from core.ram import monitor_ram
from core.hdd import monitor_hdd
from core.moth import get_motherboard_info
from core.volt import get_voltage_info


import sys, json, time, random, math, multiprocessing, subprocess


class DiagnosticThread(QThread):
    update_signal = pyqtSignal(int, str)
    finished_signal = pyqtSignal(dict, str)

    def __init__(self, model):
        super().__init__()
        self.model = model

    def run(self):
        # Сбор данных
        components = {
            'CPU': get_cpu_info(),
            'GPU': monitor_gpu(),
            'RAM': monitor_ram(),
            'HDD': monitor_hdd()
        }
        
        # Эмуляция прогресса
        for i in range(1, 101):
            time.sleep(0.03)  # Для визуализации прогресса
            self.update_signal.emit(i, "Сбор данных...")
        
        # Получение прогноза
        cpu_data = components['CPU']
        gpu_data = components['GPU'][0] if components['GPU'] else None
        
        if not all([cpu_data, gpu_data]):
            self.finished_signal.emit({}, "Ошибка сбора данных")
            return

        prediction = self.model.predict(
            cpu_usage=cpu_data.get('usage', 0),
            cpu_temp=cpu_data.get('temperatures', {}).get('coretemp', [{}])[0].get('current', 0),
            gpu_usage=gpu_data.get('load', 0),
            gpu_temp=gpu_data.get('temperature', 0),
            disk_usage=components['HDD'].get('percent', 0),
            ram_usage=components['RAM'].get('percent', 0)
        )
        
        self.finished_signal.emit(components, prediction)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Диагностика системы")
        self.setMinimumSize(800, 600)  # Минимальный размер окна
        self.setGeometry(100, 100, 1200, 800)

        # Главный виджет и макет
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)  # Отступы
        main_layout.setSpacing(10)  # Расстояние между элементами

        # Боковое меню
        self.menu_list = QListWidget()
        self.menu_list.setMinimumWidth(180)  # Минимальная ширина
        self.menu_list.setMaximumWidth(220)  # Максимальная ширина
        self.menu_list.setSizePolicy(
            QSizePolicy.Policy.Fixed, 
            QSizePolicy.Policy.Expanding
        )
        self.menu_list.itemClicked.connect(self.switch_screen)
        self.init_menu_list()
        main_layout.addWidget(self.menu_list)

        # Центральная область с контентом
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setSizePolicy(
            QSizePolicy.Policy.Expanding, 
            QSizePolicy.Policy.Expanding
        )
        main_layout.addWidget(self.stacked_widget, 1)  # Коэффициент растяжения 1

        self.setCentralWidget(main_widget)
        self.create_menus()
        
        self.init_screens()

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
        """Создаем профессиональное верхнее меню приложения."""
        menu_bar = self.menuBar()
        
        # Стилизация меню
        menu_bar.setStyleSheet("""
            QMenuBar {
                background-color: #2D2D2D;
                color: white;
                padding: 5px;
                border-bottom: 1px solid #555;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 5px 15px;
                border-radius: 4px;
            }
            QMenuBar::item:selected {
                background-color: #444;
            }
            QMenu {
                background-color: #2D2D2D;
                border: 1px solid #555;
                color: white;
            }
            QMenu::item {
                padding: 8px 25px 8px 20px;
            }
            QMenu::item:selected {
                background-color: #444;
            }
            QMenu::separator {
                height: 1px;
                background-color: #555;
                margin: 5px 0;
            }
        """)
        
        # Меню "Файл"
        file_menu = menu_bar.addMenu("Файл")
        
        save_action = QAction("Сохранить отчет", self)
        save_action.setShortcut("Ctrl+S")
        save_action.setIcon(QIcon("gui/img/save.png"))
        
        export_action = QAction("Экспорт данных", self)
        export_action.setIcon(QIcon("gui/img/export.png"))
        
        exit_action = QAction("Выход", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setIcon(QIcon("gui/img/exit.png"))
        exit_action.triggered.connect(QApplication.instance().quit)
        
        file_menu.addAction(save_action)
        file_menu.addAction(export_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)
        
        # Меню "Настройки"
        settings_menu = menu_bar.addMenu("Настройки")
        
        appearance_action = QAction("Внешний вид", self)
        appearance_action.setIcon(QIcon("gui/img/appearance.png"))
        
        notifications_action = QAction("Уведомления", self)
        notifications_action.setIcon(QIcon("gui/img/notifications.png"))
        
        system_action = QAction("Системные настройки", self)
        system_action.setIcon(QIcon("gui/img/settings.png"))
        
        settings_menu.addAction(appearance_action)
        settings_menu.addAction(notifications_action)
        settings_menu.addSeparator()
        settings_menu.addAction(system_action)
        
        # Меню "Отчет"
        report_menu = menu_bar.addMenu("Отчет")
        
        generate_action = QAction("Создать отчет", self)
        generate_action.setShortcut("Ctrl+R")
        generate_action.setIcon(QIcon("gui/img/report.png"))
        
        history_action = QAction("История отчетов", self)
        history_action.setIcon(QIcon("gui/img/history.png"))
        
        report_menu.addAction(generate_action)
        report_menu.addAction(history_action)
        
        # Меню "Помощь"
        help_menu = menu_bar.addMenu("Помощь")
        
        docs_action = QAction("Документация", self)
        docs_action.setShortcut("F1")
        docs_action.setIcon(QIcon("gui/img/docs.png"))
        
        support_action = QAction("Техническая поддержка", self)
        support_action.setIcon(QIcon("gui/img/support.png"))
        
        forum_action = QAction("Форум пользователей", self)
        forum_action.setIcon(QIcon("gui/img/forum.png"))
        
        help_menu.addAction(docs_action)
        help_menu.addAction(support_action)
        help_menu.addAction(forum_action)
        
        # Меню "О приложении"
        about_menu = menu_bar.addMenu("О приложении")
        
        about_action = QAction("О программе", self)
        about_action.setIcon(QIcon("gui/img/info.png"))
        about_action.triggered.connect(self.show_about)
        
        update_action = QAction("Проверить обновления", self)
        update_action.setIcon(QIcon("gui/img/update.png"))
        
        license_action = QAction("Лицензия", self)
        license_action.setIcon(QIcon("gui/img/license.png"))
        
        contributors_action = QAction("Разработчики", self)
        contributors_action.setIcon(QIcon("gui/img/contributors.png"))
        
        about_menu.addAction(about_action)
        about_menu.addAction(update_action)
        about_menu.addAction(license_action)
        about_menu.addAction(contributors_action)

    def show_about(self):
        """Отображение диалогового окна 'О приложении'."""
        about_text = (
            "<h2>Диагностика системы</h2>"
            "<p>Версия: 1.0.0</p>"
            "<p>Создано с помощью энтузиазма и кофе</p>"
            "<p>Приложение для комплексной диагностики и мониторинга системы</p>"
            "<p>© 2023 Дипломный проект</p>"
            "<hr>"
            "<p>Совместимо с Linux дистрибутивами:</p>"
            "<ul>"
            "<li>Ubuntu/Debian</li>"
            "<li>Fedora/RHEL</li>"
            "<li>Astra Linux</li>"
            "<li>RED OS Linux</li>"
            "</ul>"
            "<p>Особенности приложения:</p>"
            "<ul>"
            "<li>Подробная диагностика всех компонентов системы</li>"
            "<li>Мониторинг в реальном времени</li>"
            "<li>Тестирование производительности</li>"
            "<li>Генерация отчетов</li>"
            "<li>Рекомендации по оптимизации</li>"
            "</ul>"
        )
        
        about_dialog = QMessageBox(self)
        about_dialog.setWindowTitle("О приложении")
        about_dialog.setIconPixmap(QPixmap("gui/img/logo.png").scaled(100, 100, 
            Qt.AspectRatioMode.KeepAspectRatio, 
            Qt.TransformationMode.SmoothTransformation))
        about_dialog.setTextFormat(Qt.TextFormat.RichText)
        about_dialog.setText(about_text)
        
        # Добавляем кнопку "Подробнее"
        more_button = about_dialog.addButton("Подробнее", QMessageBox.ButtonRole.ActionRole)
        more_button.clicked.connect(self.show_additional_info)
        
        about_dialog.exec()

    def show_additional_info(self):
        """Показывает дополнительную информацию о приложении"""
        info_text = (
            "<h3>Технические детали</h3>"
            "<p><b>Разработка:</b></p>"
            "<ul>"
            "<li>Python 3.10+</li>"
            "<li>PyQt 6</li>"
            "<li>psutil, pysensors, nvidia-ml-py3</li>"
            "</ul>"
            "<p><b>Системные требования:</b></p>"
            "<ul>"
            "<li>Процессор: x86-64 или ARMv8</li>"
            "<li>ОЗУ: 512 МБ минимум</li>"
            "<li>Диск: 500 МБ свободного места</li>"
            "</ul>"
            "<p><b>Лицензия:</b> GNU GPL v3.0</p>"
            "<p><b>Исходный код:</b> доступен на GitHub</p>"
            "<hr>"
            "<p>Приложение создано студентом в рамках дипломного проекта</p>"
            "<p>Особая благодарность кофеину за вдохновение и поддержку</p>"
        )
        
        QMessageBox.information(
            self,
            "Дополнительная информация",
            info_text,
            QMessageBox.StandardButton.Ok
        )

    def init_screens(self):
        """Инициализация экранов для QStackedWidget."""
        self.general_info_screen = self.create_general_screen()
        self.processor_screen = self.CPU_info_screen("Процессор", "Информация о процессоре.", "gui/img/cpu.png")
        self.memory_screen = self.RAM_info_screen("Оперативная память", "Информация о памяти.", "gui/img/ram.png")
        self.disk_screen = self.HDD_info_screen("Дисковая подсистема", "Информация о дисках.", "gui/img/disk.png")
        self.gpu_screen = self.GPU_info_screen("Видеокарта", "Информация о видеокарте.", "gui/img/gpu.png")
        self.motherboard_screen = self.MB_info_screen("Материнская плата", "Информация о материнской плате.", "gui/img/motherboard.png")
        self.voltage_screen = self.Voltage_info_screen("Напряжение", "Информация о напряжении.", "gui/img/volt.png")
        self.diagnostic_screen = self.create_diagnostic_screen("Диагностика", "Режим диагностики системы.", "gui/img/diag.png")
        self.testing_screen = self.create_testing_screen("Тестирование", "Тестирование системы на устойчивость.", "gui/img/test.png")
        
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
        screen_layout = QVBoxLayout(screen)
        screen_layout.setContentsMargins(20, 20, 20, 20)
        screen_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Контейнер для карточек
        container = QWidget()
        grid_layout = QGridLayout(container)
        grid_layout.setSpacing(20)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        
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

        # Адаптивное количество колонок
        columns = max(2, min(4, self.width() // 250))
        
        # Создаем карточки
        for i, (title, icon_path) in enumerate(cards):
            # Контейнер для карточки
            card = QFrame()
            card.setFixedSize(180, 180)
            card.setStyleSheet("""
                QFrame {
                    background-color: #2D2D2D;  /* Темно-серый фон */
                    border-radius: 10px;
                    border: 1px solid #555;  /* Темная обводка */
                }
                QFrame:hover {
                    background-color: #393939;  /* Слегка светлее при наведении */
                    border: 1px solid #777;  /* Светлее обводка при наведении */
                }
            """)
            
            # Макет для содержимого карточки
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(10, 10, 10, 10)
            card_layout.setSpacing(8)
            
            # Иконка
            if icon_path:
                icon_label = QLabel()
                pixmap = QPixmap(icon_path).scaled(64, 64, 
                    Qt.AspectRatioMode.KeepAspectRatio, 
                    Qt.TransformationMode.SmoothTransformation
                )
                icon_label.setPixmap(pixmap)
                icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                card_layout.addWidget(icon_label)
            
            # Текст с переносом - белый цвет для контраста
            text_label = QLabel(title)
            text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            text_label.setWordWrap(True)
            text_label.setStyleSheet("""
                font-weight: bold; 
                font-size: 14px; 
                border: none;
                color: #FFFFFF;  /* Белый текст */
            """)
            card_layout.addWidget(text_label)
            
            # Растяжка для центрирования
            card_layout.addStretch()
            
            # Создаем кнопку-оверлей для обработки кликов
            overlay_button = QPushButton(card)
            overlay_button.setGeometry(0, 0, 180, 180)
            overlay_button.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                }
                QPushButton:hover {
                    background-color: transparent;
                    border: none;
                }
            """)
            overlay_button.clicked.connect(lambda _, t=title: self.switch_screen_by_title(t))
            
            row = i // columns
            col = i % columns
            grid_layout.addWidget(card, row, col, alignment=Qt.AlignmentFlag.AlignCenter)
        
        screen_layout.addWidget(container, alignment=Qt.AlignmentFlag.AlignCenter)
        screen_layout.addStretch()
        
        return screen
    
    def run_test(self, test_type):
        """Запуск тестирования"""
        # Сохраняем текущее состояние
        self.before_state = self.get_system_state()
        self.update_test_results(self.before_state, self.before_test_group)
        
        # Блокируем кнопки
        for btn in [self.test_cpu_btn, self.test_ram_btn, self.test_gpu_btn, self.test_all_btn]:
            btn.setEnabled(False)
        
        self.test_progress.setVisible(True)
        self.test_progress.setValue(0)
        
        # Запуск тестов в отдельном процессе
        self.test_process = QProcess()
        self.test_process.finished.connect(self.on_test_finished)
        
        # Определяем какой тест запускать
        if test_type == 'cpu':
            script = 'test/testing_CPU.py'
        elif test_type == 'ram':
            script = 'test/testing_RAM.py'
        elif test_type == 'gpu':
            script = 'test/testing_GPU.py'
        else:  # all
            script = 'test/testing_ALL.py'
        
        self.test_process.start('python', [script])
        
        # Таймер для прогресса
        self.test_time = 0
        self.test_timer_progress = QTimer()
        self.test_timer_progress.timeout.connect(self.update_test_progress)
        self.test_timer_progress.start(1000)

    def update_test_progress(self):
        """Обновление прогресса тестирования"""
        self.test_time += 1
        progress = min(100, int((self.test_time / 60) * 100))
        self.test_progress.setValue(progress)
        
        if self.test_time >= 60:
            self.test_timer_progress.stop()

    def on_test_finished(self):
        """Обработка завершения теста"""
        # Получаем состояние после теста
        self.after_state = self.get_system_state()
        self.update_test_results(self.after_state, self.after_test_group)
        
        # Разблокируем кнопки
        for btn in [self.test_cpu_btn, self.test_ram_btn, self.test_gpu_btn, self.test_all_btn]:
            btn.setEnabled(True)
        
        self.test_progress.setVisible(False)
        self.test_timer_progress.stop()

    def get_system_state(self):
        """Получение текущего состояния системы"""
        state = {
            'CPU': get_cpu_info(),
            'RAM': monitor_ram(),
            'GPU': monitor_gpu()[0] if monitor_gpu() else {},
            'HDD': monitor_hdd()
        }
        return state

    def update_test_results(self, state, group):
        """Обновление результатов тестирования"""
        # Очищаем предыдущие результаты
        if group.layout():
            while group.layout().count():
                item = group.layout().takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
        
        # Создаем новый layout
        layout = QFormLayout()
        
        # Добавляем данные CPU
        cpu = state.get('CPU', {})
        layout.addRow(QLabel("<b>Процессор:</b>"))
        layout.addRow("Загрузка:", QLabel(f"{cpu.get('usage', 'N/A')}%"))
        if cpu.get('temperatures'):
            for sensor, entries in cpu['temperatures'].items():
                for entry in entries:
                    layout.addRow(
                        f"{entry['label']}:", 
                        QLabel(f"{entry['current']}°C (макс {entry['high']})")
                    )
        
        # Добавляем данные RAM
        ram = state.get('RAM', {})
        layout.addRow(QLabel("<b>Память:</b>"))
        layout.addRow("Использовано:", QLabel(f"{ram.get('percent', 'N/A')}%"))
        layout.addRow("Доступно:", QLabel(f"{ram.get('free', 'N/A')} ГБ"))
        
        # Добавляем данные GPU
        gpu = state.get('GPU', {})
        layout.addRow(QLabel("<b>Видеокарта:</b>"))
        layout.addRow("Загрузка:", QLabel(f"{gpu.get('load', 'N/A')}%"))
        layout.addRow("Температура:", QLabel(f"{gpu.get('temperature', 'N/A')}°C"))
        
        # Добавляем данные HDD
        hdd = state.get('HDD', {})
        layout.addRow(QLabel("<b>Диск:</b>"))
        layout.addRow("Использовано:", QLabel(f"{hdd.get('percent', 'N/A')}%"))
        
        group.setLayout(layout)

    def update_test_status(self):
        """Обновление статуса системы в реальном времени"""
        if not hasattr(self, 'before_state'):
            self.before_state = self.get_system_state()
            self.update_test_results(self.before_state, self.before_test_group)
    
    def CPU_info_screen(self, title, description, image_path=None):
        screen = QWidget()
        main_layout = QVBoxLayout(screen)

        # Изображение процессора
        image_label = QLabel(self)
        pixmap = QPixmap("gui/img/cpu.png")
        image_label.setPixmap(pixmap.scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio))
        main_layout.addWidget(image_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Заголовок
        title_label = QLabel("<h1>Процессор</h1>", self)
        main_layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Создаем скроллируемую область для данных
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        self.cpu_info_layout = QVBoxLayout(content)
        scroll.setWidget(content)
        main_layout.addWidget(scroll)

        # Таймер обновления
        self.cpu_timer = QTimer()
        self.cpu_timer.timeout.connect(self.update_cpu_info)
        self.cpu_timer.start(500)  # обновление каждые 0.5 секунды

        return screen

    def update_cpu_info(self):
        """Обновление информации о процессоре с улучшенным дизайном"""
        cpu_data = get_cpu_info()  # Получаем словарь

        # Очищаем контейнер перед обновлением
        while self.cpu_info_layout.count():
            item = self.cpu_info_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        if "error" in cpu_data:
            error_label = QLabel(f"Ошибка: {cpu_data['error']}")
            error_label.setStyleSheet("color: red; font-weight: bold;")
            self.cpu_info_layout.addWidget(error_label, alignment=Qt.AlignmentFlag.AlignCenter)
            return

        # Основные параметры
        main_group = QGroupBox("Основные параметры")
        main_layout = QFormLayout()
        main_layout.addRow("Загрузка:", self._create_colored_label(f"{cpu_data['usage']}%", 'percent'))
        main_layout.addRow("Ядра:", QLabel(str(cpu_data['cores'])))
        main_layout.addRow("Потоки:", QLabel(str(cpu_data['threads'])))
        main_layout.addRow("Текущая частота:", QLabel(f"{cpu_data['freq_current']} MHz"))
        main_layout.addRow("Минимальная частота:", QLabel(f"{cpu_data['freq_min']} MHz"))
        main_layout.addRow("Максимальная частота:", QLabel(f"{cpu_data['freq_max']} MHz"))
        main_group.setLayout(main_layout)
        self.cpu_info_layout.addWidget(main_group)

        # Температуры
        if cpu_data["temperatures"]:
            temp_group = QGroupBox("Температуры")
            temp_layout = QFormLayout()
            
            for sensor, entries in cpu_data["temperatures"].items():
                # Добавляем разделитель между сенсорами
                if temp_layout.rowCount() > 0:
                    separator = QFrame()
                    separator.setFrameShape(QFrame.Shape.HLine)
                    separator.setFrameShadow(QFrame.Shadow.Sunken)
                    temp_layout.addRow(separator)
                
                for entry in entries:
                    label = entry['label']
                    current = entry['current']
                    high = entry.get('high', 'N/A')
                    critical = entry.get('critical', 'N/A')
                    
                    temp_layout.addRow(
                        f"{label}:", 
                        self._create_colored_label(f"{current}°C (макс: {high}, крит: {critical})", 'temp')
                    )
            
            temp_group.setLayout(temp_layout)
            self.cpu_info_layout.addWidget(temp_group)

        # Добавляем растяжку в конце
        self.cpu_info_layout.addStretch()
        
    def GPU_info_screen(self, title, description, image_path=None):
        screen = QWidget()
        main_layout = QVBoxLayout(screen)

        # Изображение видеокарты
        image_label = QLabel(self)
        pixmap = QPixmap("gui/img/gpu.png")
        image_label.setPixmap(pixmap.scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio))
        main_layout.addWidget(image_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Заголовок
        title_label = QLabel("<h1>Видеокарта</h1>", self)
        main_layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Создаем скроллируемую область для данных
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        self.gpu_info_layout = QVBoxLayout(content)
        scroll.setWidget(content)
        main_layout.addWidget(scroll)

        # Таймер для обновления данных
        self.gpu_timer = QTimer()
        self.gpu_timer.timeout.connect(self.update_gpu_info)
        self.gpu_timer.start(500)  # Обновление каждую секунду

        return screen

    def update_gpu_info(self):
        """Обновление информации о видеокарте с улучшенным дизайном"""
        gpu_data_list = monitor_gpu()

        # Очищаем контейнер перед обновлением
        while self.gpu_info_layout.count():
            item = self.gpu_info_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        if not gpu_data_list:
            error_label = QLabel("Ошибка: Не удалось получить данные о видеокарте")
            error_label.setStyleSheet("color: red; font-weight: bold;")
            self.gpu_info_layout.addWidget(error_label, alignment=Qt.AlignmentFlag.AlignCenter)
            return

        for i, gpu_data in enumerate(gpu_data_list):
            # Группа для каждой видеокарты
            gpu_group = QGroupBox(f"Видеокарта {i}: {gpu_data.get('gpu', 'Неизвестно')}")
            gpu_layout = QFormLayout()
            
            # Основные параметры
            gpu_layout.addRow("Загрузка GPU:", self._create_colored_label(f"{gpu_data['load']}%", 'percent'))
            gpu_layout.addRow("Загрузка памяти:", self._create_colored_label(f"{gpu_data['ram_load']}%", 'percent'))
            gpu_layout.addRow("Температура:", self._create_colored_label(f"{gpu_data['temperature']}°C", 'temp'))
            gpu_layout.addRow("Частота чипа:", QLabel(f"{gpu_data['chip']} МГц"))
            
            # Дополнительные параметры, если есть
            if 'memory_total' in gpu_data:
                gpu_layout.addRow("Объем памяти:", QLabel(f"{gpu_data['memory_total']} МБ"))
            if 'memory_used' in gpu_data:
                gpu_layout.addRow("Использовано памяти:", QLabel(f"{gpu_data['memory_used']} МБ"))
            if 'memory_free' in gpu_data:
                gpu_layout.addRow("Свободно памяти:", QLabel(f"{gpu_data['memory_free']} МБ"))
            
            gpu_group.setLayout(gpu_layout)
            self.gpu_info_layout.addWidget(gpu_group)

        # Добавляем растяжку в конце
        self.gpu_info_layout.addStretch()
    
    def MB_info_screen(self, title, description, image_path=None):
        screen = QWidget()
        main_layout = QVBoxLayout(screen)

        # Изображение материнской платы
        image_label = QLabel(self)
        pixmap = QPixmap("gui/img/motherboard.png")
        image_label.setPixmap(pixmap.scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio))
        main_layout.addWidget(image_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Заголовок
        title_label = QLabel("<h1>Материнская плата</h1>", self)
        main_layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Создаем скроллируемую область для данных
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        self.mb_info_layout = QVBoxLayout(content)
        scroll.setWidget(content)
        main_layout.addWidget(scroll)

        # Таймер обновления
        self.mb_timer = QTimer()
        self.mb_timer.timeout.connect(self.update_mb_info)
        self.mb_timer.start(5000)  # обновление каждые 5 секунд (данные обычно статичны)

        return screen

    def update_mb_info(self):
        """Обновление информации о материнской плате с улучшенным дизайном"""
        mb_data = get_motherboard_info()

        # Очищаем контейнер перед обновлением
        while self.mb_info_layout.count():
            item = self.mb_info_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        if "error" in mb_data:
            error_label = QLabel(f"Ошибка: {mb_data['error']}")
            error_label.setStyleSheet("color: red; font-weight: bold;")
            self.mb_info_layout.addWidget(error_label, alignment=Qt.AlignmentFlag.AlignCenter)
            return

        # Основные параметры платы
        board_group = QGroupBox("Параметры платы")
        board_layout = QFormLayout()
        board_layout.addRow("Производитель:", QLabel(mb_data.get('manufacturer', 'Неизвестно')))
        board_layout.addRow("Модель:", QLabel(mb_data.get('product', 'Неизвестно')))
        board_layout.addRow("Версия:", QLabel(mb_data.get('version', 'Неизвестно')))
        board_layout.addRow("Серийный номер:", QLabel(mb_data.get('serial', 'Неизвестно')))
        board_layout.addRow("Чипсет:", QLabel(mb_data.get('chipset', 'Неизвестно')))
        board_group.setLayout(board_layout)
        self.mb_info_layout.addWidget(board_group)

        # Информация о BIOS
        bios_group = QGroupBox("BIOS")
        bios_layout = QFormLayout()
        bios_layout.addRow("Производитель:", QLabel(mb_data.get('bios_vendor', 'Неизвестно')))
        bios_layout.addRow("Версия:", QLabel(mb_data.get('bios_version', 'Неизвестно')))
        bios_layout.addRow("Дата:", QLabel(mb_data.get('bios_date', 'Неизвестно')))
        bios_layout.addRow("Размер:", QLabel(mb_data.get('bios_size', 'Неизвестно')))
        bios_group.setLayout(bios_layout)
        self.mb_info_layout.addWidget(bios_group)

        # Слоты расширения
        if 'slots' in mb_data and mb_data['slots']:
            slots_group = QGroupBox("Слоты расширения")
            slots_layout = QFormLayout()
            
            for i, slot in enumerate(mb_data['slots']):
                slot_layout = QFormLayout()
                slot_layout.addRow("Тип:", QLabel(slot.get('type', 'N/A')))
                slot_layout.addRow("Статус:", QLabel("Занят" if slot.get('occupied') else "Свободен"))
                slot_layout.addRow("Описание:", QLabel(slot.get('description', 'N/A')))
                
                # Добавляем разделитель между слотами
                if i > 0:
                    separator = QFrame()
                    separator.setFrameShape(QFrame.Shape.HLine)
                    separator.setFrameShadow(QFrame.Shadow.Sunken)
                    slots_layout.addRow(separator)
                
                slots_layout.addRow(f"Слот {i+1}:", slot_layout)
            
            slots_group.setLayout(slots_layout)
            self.mb_info_layout.addWidget(slots_group)

        # Датчики температуры (если доступны)
        if 'temperatures' in mb_data and mb_data['temperatures']:
            temp_group = QGroupBox("Температуры")
            temp_layout = QFormLayout()
            
            for sensor, temp in mb_data['temperatures'].items():
                temp_layout.addRow(
                    f"{sensor}:", 
                    self._create_colored_label(f"{temp}°C", 'temp')
                )
            
            temp_group.setLayout(temp_layout)
            self.mb_info_layout.addWidget(temp_group)

        # Добавляем растяжку в конце
        self.mb_info_layout.addStretch()
        
    def Voltage_info_screen(self, title, description, image_path=None):
        screen = QWidget()
        main_layout = QVBoxLayout(screen)

        # Изображение напряжения
        image_label = QLabel(self)
        pixmap = QPixmap("gui/img/volt.png")
        image_label.setPixmap(pixmap.scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio))
        main_layout.addWidget(image_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Заголовок
        title_label = QLabel("<h1>Напряжение</h1>", self)
        main_layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Создаем скроллируемую область для данных
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        self.voltage_info_layout = QVBoxLayout(content)
        scroll.setWidget(content)
        main_layout.addWidget(scroll)

        # Таймер для обновления данных
        self.voltage_timer = QTimer()
        self.voltage_timer.timeout.connect(self.update_voltage_info)
        self.voltage_timer.start(2000)  # Обновление каждые 2 секунды

        return screen

    def update_voltage_info(self):
        """Обновление информации о напряжении с улучшенным дизайном"""
        voltage_info = get_voltage_info()

        # Очищаем контейнер перед обновлением
        while self.voltage_info_layout.count():
            item = self.voltage_info_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        if not voltage_info:
            error_label = QLabel("Ошибка: Не удалось получить данные о напряжении")
            error_label.setStyleSheet("color: red; font-weight: bold;")
            self.voltage_info_layout.addWidget(error_label, alignment=Qt.AlignmentFlag.AlignCenter)
            return
            
        if "error" in voltage_info:
            error_label = QLabel(f"Ошибка: {voltage_info['error']}")
            error_label.setStyleSheet("color: red; font-weight: bold;")
            self.voltage_info_layout.addWidget(error_label, alignment=Qt.AlignmentFlag.AlignCenter)
            return

        # Группа для батареи
        battery_group = QGroupBox("Состояние батареи")
        battery_layout = QFormLayout()
        
        battery = voltage_info.get('battery', {})
        if battery:
            battery_layout.addRow("Питание от сети:", QLabel("Да" if battery.get('power_plugged') else "Нет"))
            battery_layout.addRow("Заряд:", self._create_colored_label(f"{battery.get('percent', 'Нет данных')}%", 'percent'))
            
            secsleft = battery.get('secsleft')
            if secsleft is not None:
                if secsleft == -1:
                    battery_layout.addRow("Оставшееся время:", QLabel("Расчитывается..."))
                elif secsleft == -2:
                    battery_layout.addRow("Оставшееся время:", QLabel("Неограничено"))
                else:
                    mins, secs = divmod(secsleft, 60)
                    hours, mins = divmod(mins, 60)
                    battery_layout.addRow("Оставшееся время:", QLabel(f"{hours:02d}:{mins:02d}:{secs:02d}"))
        else:
            battery_layout.addRow("Статус:", QLabel("Батарея не обнаружена"))
            
        battery_group.setLayout(battery_layout)
        self.voltage_info_layout.addWidget(battery_group)

        # Группа для напряжений
        voltages_group = QGroupBox("Напряжения компонентов")
        voltages_layout = QFormLayout()
        
        voltages = voltage_info.get('voltages', {})
        voltages_layout.addRow("CPU:", QLabel(voltages.get('cpu_voltage', 'Нет данных')))
        voltages_layout.addRow("GPU:", QLabel(voltages.get('gpu_voltage', 'Нет данных')))
        voltages_layout.addRow("RAM:", QLabel(voltages.get('ram_voltage', 'Нет данных')))
        voltages_layout.addRow("3.3V:", QLabel(voltages.get('3v3_voltage', 'Нет данных')))
        voltages_layout.addRow("5V:", QLabel(voltages.get('5v_voltage', 'Нет данных')))
        voltages_layout.addRow("12V:", QLabel(voltages.get('12v_voltage', 'Нет данных')))
        
        voltages_group.setLayout(voltages_layout)
        self.voltage_info_layout.addWidget(voltages_group)

        # Добавляем растяжку в конце
        self.voltage_info_layout.addStretch()
        
    def RAM_info_screen(self, title, description, image_path=None):
        screen = QWidget()
        main_layout = QVBoxLayout(screen)

        # Изображение оперативной памяти
        image_label = QLabel(self)
        pixmap = QPixmap("gui/img/ram.png")
        image_label.setPixmap(pixmap.scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio))
        main_layout.addWidget(image_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Заголовок
        title_label = QLabel("<h1>Оперативная память</h1>", self)
        main_layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Создаем скроллируемую область для данных
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        self.ram_info_layout = QVBoxLayout(content)
        scroll.setWidget(content)
        main_layout.addWidget(scroll)

        # Таймер для обновления данных
        self.ram_timer = QTimer()
        self.ram_timer.timeout.connect(self.update_ram_info)
        self.ram_timer.start(500)

        return screen

    def update_ram_info(self):
        """Обновление информации об оперативной памяти с улучшенным дизайном"""
        ram_info = monitor_ram()

        # Очищаем контейнер перед обновлением
        while self.ram_info_layout.count():
            item = self.ram_info_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        if not ram_info:
            error_label = QLabel("Ошибка: Не удалось получить данные о RAM")
            error_label.setStyleSheet("color: red; font-weight: bold;")
            self.ram_info_layout.addWidget(error_label, alignment=Qt.AlignmentFlag.AlignCenter)
            return

        # Основные параметры
        main_group = QGroupBox("Основные параметры")
        main_layout = QFormLayout()
        main_layout.addRow("Общий объем:", QLabel(f"{ram_info['ram']} ГБ"))
        main_layout.addRow("Свободно:", QLabel(f"{ram_info['free']} ГБ"))
        main_layout.addRow("Используется:", QLabel(f"{ram_info['usage']} ГБ"))
        main_layout.addRow("Занято:", self._create_colored_label(f"{ram_info['percent']}%", 'percent'))
        main_group.setLayout(main_layout)
        self.ram_info_layout.addWidget(main_group)

        # Детализация по слотам, если есть
        if 'slots' in ram_info and ram_info['slots']:
            slots_group = QGroupBox("Слоты памяти")
            slots_layout = QFormLayout()
            
            for i, slot in enumerate(ram_info['slots']):
                slot_layout = QFormLayout()
                slot_layout.addRow("Размер:", QLabel(f"{slot.get('size', 'N/A')} ГБ"))
                slot_layout.addRow("Тип:", QLabel(slot.get('type', 'N/A')))
                slot_layout.addRow("Скорость:", QLabel(f"{slot.get('speed', 'N/A')} МГц"))
                slot_layout.addRow("Производитель:", QLabel(slot.get('manufacturer', 'N/A')))
                slot_layout.addRow("Серийный номер:", QLabel(slot.get('serial', 'N/A')))
                
                # Добавляем разделитель между слотами
                if i > 0:
                    separator = QFrame()
                    separator.setFrameShape(QFrame.Shape.HLine)
                    separator.setFrameShadow(QFrame.Shadow.Sunken)
                    slots_layout.addRow(separator)
                
                slots_layout.addRow(f"Слот {i+1}:", slot_layout)
            
            slots_group.setLayout(slots_layout)
            self.ram_info_layout.addWidget(slots_group)

        # Добавляем растяжку в конце
        self.ram_info_layout.addStretch()
        
    def HDD_info_screen(self, title, description, image_path=None):
        screen = QWidget()
        main_layout = QVBoxLayout(screen)

        # Изображение диска
        image_label = QLabel(self)
        pixmap = QPixmap("gui/img/disk.png")
        image_label.setPixmap(pixmap.scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio))
        main_layout.addWidget(image_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Заголовок
        title_label = QLabel("<h1>Диск</h1>", self)
        main_layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Создаем скроллируемую область для данных
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        self.hdd_info_layout = QVBoxLayout(content)
        scroll.setWidget(content)
        main_layout.addWidget(scroll)

        # Таймер для обновления данных
        self.hdd_timer = QTimer()
        self.hdd_timer.timeout.connect(self.update_hdd_info)
        self.hdd_timer.start(500)

        return screen

    def update_hdd_info(self):
        """Обновление информации о дисках с улучшенным дизайном"""
        hdd_info = monitor_hdd()  # Изменено название переменной (не список)

        # Очищаем контейнер перед обновлением
        while self.hdd_info_layout.count():
            item = self.hdd_info_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        # Обрабатываем случай с ошибкой получения данных
        if not hdd_info:
            error_label = QLabel("Ошибка: Не удалось получить данные о дисках")
            error_label.setStyleSheet("color: red; font-weight: bold;")
            self.hdd_info_layout.addWidget(error_label, alignment=Qt.AlignmentFlag.AlignCenter)
            return

        # Основная группа для диска
        disk_group = QGroupBox(f"Диск: {hdd_info.get('device', 'Неизвестно')}")
        disk_layout = QFormLayout()
        
        # Основные параметры
        disk_layout.addRow("Точка подключения:", QLabel(hdd_info['mountpoint']))
        disk_layout.addRow("Тип файловой системы:", QLabel(hdd_info['file_sys']))
        disk_layout.addRow("Общий объем:", QLabel(f"{hdd_info['size']} ГБ"))
        disk_layout.addRow("Использовано:", QLabel(f"{hdd_info['used']} ГБ"))
        disk_layout.addRow("Свободно:", QLabel(f"{hdd_info['free']} ГБ"))
        disk_layout.addRow("Процент использования:", self._create_colored_label(f"{hdd_info['percent']}%", 'percent'))
        
        # SMART информация, если доступна
        if 'smart' in hdd_info and hdd_info['smart']:
            smart_group = QGroupBox("SMART статус")
            smart_layout = QFormLayout()
            
            smart_layout.addRow("Статус:", QLabel(hdd_info['smart']['status']))
            smart_layout.addRow("Температура:", self._create_colored_label(
                f"{hdd_info['smart'].get('temperature', 'N/A')}°C", 'temp'))
            smart_layout.addRow("Время работы:", QLabel(f"{hdd_info['smart'].get('power_on_hours', 'N/A')} часов"))
            smart_layout.addRow("Ошибки чтения:", QLabel(str(hdd_info['smart'].get('read_errors', 'N/A'))))
            
            smart_group.setLayout(smart_layout)
            disk_layout.addRow(smart_group)
        
        disk_group.setLayout(disk_layout)
        self.hdd_info_layout.addWidget(disk_group)

        # Добавляем растяжку в конце
        self.hdd_info_layout.addStretch()
        
    def create_diagnostic_screen(self, title, description, image_path=None):
        """Создаем экран диагностики с улучшенным дизайном"""
        screen = QWidget()
        main_layout = QVBoxLayout(screen)
        
        # Стилизация
        self.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                border: 1px solid #ddd;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px;
            }
        """)
        
        # Кнопка запуска
        self.diagnose_btn = QPushButton("Запустить диагностику")
        self.diagnose_btn.setStyleSheet("""
            QPushButton {
                background-color: #474A51;
                color: white;
                border: none;
                padding: 10px;
                font-size: 16px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #A9A9AA;
            }
        """)
        self.diagnose_btn.setFixedHeight(50)
        self.diagnose_btn.clicked.connect(self.start_diagnosis)
        
        # Прогресс-бар
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setVisible(False)
        
        # Основная область с прокруткой
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        content_layout = QVBoxLayout(content)
        
        # Группа результатов
        self.results_group = QGroupBox("Результаты диагностики")
        results_layout = QVBoxLayout()
        
        # Подгруппы для каждого компонента
        self.cpu_group = QGroupBox("Процессор")
        self.gpu_group = QGroupBox("Видеокарта")
        self.ram_group = QGroupBox("Память")
        self.disk_group = QGroupBox("Диск")
        self.verdict_group = QGroupBox("Общий статус")
        
        # Заполняем пустые группы
        for group in [self.cpu_group, self.gpu_group, self.ram_group, self.disk_group, self.verdict_group]:
            group.setLayout(QVBoxLayout())
            group.layout().addWidget(QLabel("Данные отсутствуют"))
            results_layout.addWidget(group)
        
        self.results_group.setLayout(results_layout)
        content_layout.addWidget(self.results_group)
        scroll.setWidget(content)
        
        # Собираем основной layout
        main_layout.addWidget(self.diagnose_btn)
        main_layout.addWidget(self.progress_bar)
        main_layout.addWidget(scroll)
        
        self.diagnostic_model = DiagnosticModel()
        
        return screen

    def start_diagnosis(self):
        """Запуск диагностики в отдельном потоке"""
        self.diagnose_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        
        # Очищаем предыдущие результаты
        for group in [self.cpu_group, self.gpu_group, self.ram_group, self.disk_group, self.verdict_group]:
            while group.layout().count():
                item = group.layout().takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            label = QLabel("Идет сбор данных...")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            group.layout().addWidget(label)
        
        self.diagnostic_thread = DiagnosticThread(self.diagnostic_model)
        self.diagnostic_thread.update_signal.connect(
            lambda v, m: self.update_progress(v, m))
        self.diagnostic_thread.finished_signal.connect(self.show_results)
        self.diagnostic_thread.start()
        
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_system_status)
        self.status_timer.start(1000)

    def show_results(self, data, verdict):
        """Показывает результаты в новом формате"""
        self.diagnose_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        # Очищаем предыдущие результаты
        for group in [self.cpu_group, self.gpu_group, self.ram_group, self.disk_group, self.verdict_group]:
            layout = group.layout()
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
        
        # Цвет статуса
        color = {
            "Normal": "#2ecc71",
            "Warning": "#f39c12",
            "Critical": "#e74c3c"
        }.get(verdict, "#3498db")
        
        # Заполняем данные
        if not data:
            for group in [self.cpu_group, self.gpu_group, self.ram_group, self.disk_group]:
                group.layout().addWidget(QLabel("Ошибка сбора данных"))
            return
        
        # Процессор
        cpu = data['CPU']
        cpu_widget = QWidget()
        cpu_layout = QFormLayout(cpu_widget)
        cpu_layout.addRow("Загрузка:", QLabel(f"{cpu.get('usage', 'N/A')}%"))
        if cpu.get('temperatures'):
            for sensor, entries in cpu['temperatures'].items():
                for entry in entries:
                    cpu_layout.addRow(
                        f"{entry['label']}:",
                        QLabel(f"{entry['current']}°C")
                    )
        self.cpu_group.layout().addWidget(cpu_widget)
        
        # Видеокарта
        gpu = data['GPU'][0] if data['GPU'] else {}
        gpu_widget = QWidget()
        gpu_layout = QFormLayout(gpu_widget)
        gpu_layout.addRow("Загрузка:", QLabel(f"{gpu.get('load', 'N/A')}%"))
        gpu_layout.addRow("Температура:", QLabel(f"{gpu.get('temperature', 'N/A')}°C"))
        self.gpu_group.layout().addWidget(gpu_widget)
        
        # Память
        ram = data['RAM']
        ram_widget = QWidget()
        ram_layout = QFormLayout(ram_widget)
        ram_layout.addRow("Использовано:", QLabel(f"{ram.get('percent', 'N/A')}%"))
        ram_layout.addRow("Доступно:", QLabel(f"{ram.get('free', 'N/A')} ГБ"))
        self.ram_group.layout().addWidget(ram_widget)
        
        # Диск
        hdd = data['HDD']
        disk_widget = QWidget()
        disk_layout = QFormLayout(disk_widget)
        disk_layout.addRow("Использовано:", QLabel(f"{hdd.get('percent', 'N/A')}%"))
        self.disk_group.layout().addWidget(disk_widget)
        
        # Статус
        verdict_label = QLabel(f"""
            <div style='color: {color}; font-size: 18px; text-align: center;'>
                <b>Статус: {verdict}</b>
            </div>
        """)
        verdict_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        details_btn = QPushButton("ℹ️ Подробнее о диагностике")
        details_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
            }}
        """)
        details_btn.clicked.connect(lambda: self.show_diagnosis_details(verdict))
        
        self.verdict_group.layout().addWidget(verdict_label)
        self.verdict_group.layout().addWidget(details_btn)
            
    def show_diagnosis_details(self, verdict):
        """Подробная информация о диагностике"""
        details = {
            "Normal": "Все параметры системы в пределах нормы. Температуры и загрузка компонентов не превышают критических значений.",
            "Warning": "Обнаружены параметры, близкие к предельным. Рекомендуется проверить:\n- Температуру процессора/видеокарты\n- Загрузку оперативной памяти\n- Свободное место на диске",
            "Critical": "Критические значения параметров! Немедленно:\n1. Дайте системе остыть\n2. Закройте ресурсоемкие приложения\n3. Проверьте систему на вирусы"
        }.get(verdict, "Неизвестный статус диагностики")
        
        QMessageBox.information(
            self,
            "Подробности диагностики",
            f"<b>Объяснение статуса '{verdict}':</b><br><br>{details}",
            QMessageBox.StandardButton.Ok
        )
            
    
    def create_testing_screen(self, title, description, image_path=None):
        """Создание экрана тестирования"""
        screen = QWidget()
        layout = QVBoxLayout(screen)
        
        # Кнопки тестирования
        btn_layout = QHBoxLayout()
        self.test_cpu_btn = QPushButton("Тест CPU")
        self.test_ram_btn = QPushButton("Тест RAM")
        self.test_gpu_btn = QPushButton("Тест GPU")
        self.test_all_btn = QPushButton("Тест всего")
        
        for btn in [self.test_cpu_btn, self.test_ram_btn, self.test_gpu_btn, self.test_all_btn]:
            btn.setFixedHeight(40)
            btn.setStyleSheet("font-size: 14px;")
            btn_layout.addWidget(btn)
        
        # Прогресс-бар
        self.test_progress = QProgressBar()
        self.test_progress.setRange(0, 100)
        self.test_progress.setVisible(False)
        
        # Область результатов
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        self.results_layout = QVBoxLayout(content)
        
        # Группы результатов
        self.before_group = QGroupBox("Состояние до теста")
        self.after_group = QGroupBox("Состояние после теста")
        
        self.results_layout.addWidget(self.before_group)
        self.results_layout.addWidget(self.after_group)
        self.results_layout.addStretch()
        
        scroll.setWidget(content)
        
        # Добавляем элементы
        layout.addLayout(btn_layout)
        layout.addWidget(self.test_progress)
        layout.addWidget(scroll)
        
        # Подключение кнопок
        self.test_cpu_btn.clicked.connect(lambda: self.start_test('cpu'))
        self.test_ram_btn.clicked.connect(lambda: self.start_test('ram'))
        self.test_gpu_btn.clicked.connect(lambda: self.start_test('gpu'))
        self.test_all_btn.clicked.connect(lambda: self.start_test('all'))
        
        # Таймер обновления
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_system_status)
        self.status_timer.start(1000)
        
        return screen

    def start_test(self, test_type):
        """Запуск теста"""
        if hasattr(self, 'test_process') and self.test_process:
            #if self.test_process.state() == QProcess.ProcessState.Running:
                self.test_process.terminate()
        # Сохраняем состояние до теста
        self.before_state = self.get_system_state()
        self.update_test_results(self.before_state, self.before_group)
        
        # Блокируем кнопки
        for btn in [self.test_cpu_btn, self.test_ram_btn, self.test_gpu_btn, self.test_all_btn]:
            btn.setEnabled(False)
        
        self.test_progress.setVisible(True)
        self.test_progress.setValue(0)
        
        # Запускаем процесс
        self.test_process = QProcess()
        self.test_process.finished.connect(lambda: self.on_test_finished(test_type))
        
        script = {
            'cpu': 'testing_CPU.py',
            'ram': 'testing_RAM.py',
            'gpu': 'testing_GPU.py',
            'all': 'testing_ALL.py'
        }[test_type]
        
        self.test_process.start('python', [f'test/{script}'])
        
        # Таймер прогресса
        self.test_time = 0
        self.test_timer = QTimer()
        self.test_timer.timeout.connect(
            lambda: self.update_progress(test_type=test_type))
        self.test_timer.start(1000)

    def update_progress(self, *args, test_type=None):
        """Универсальный метод для обновления прогресса
        Args:
            - Для диагностики: (value, message)
            - Для тестирования: (test_type)
        """
        if test_type is None:
            # Режим диагностики (args = value, message)
            value, message = args
            self.progress_bar.setValue(value)
            self.progress_bar.setFormat(f"{message} {value}%")
        else:
            # Режим тестирования (args пустые, test_type содержит тип теста)
            if not hasattr(self, 'test_time'):
                self.test_time = 0
            self.test_time += 1
            progress = min(100, int((self.test_time / 60) * 100))
            self.test_progress.setValue(progress)
            
            if self.test_time >= 60:
                self.test_timer.stop()
                if hasattr(self, 'test_process') and self.test_process.state() == QProcess.ProcessState.Running:
                    self.test_process.terminate()

    def on_test_finished(self, test_type):
        """Завершение теста"""
        if hasattr(self, 'test_process'):
            self.test_process = None
        # Получаем состояние после теста
        self.after_state = self.get_system_state()
        self.update_test_results(self.after_state, self.after_group)
        
        # Разблокируем кнопки
        for btn in [self.test_cpu_btn, self.test_ram_btn, self.test_gpu_btn, self.test_all_btn]:
            btn.setEnabled(True)
        
        self.test_progress.setVisible(False)
        self.test_timer.stop()

    def update_test_results(self, state, group):
        """Обновление результатов теста с группировкой параметров"""
        # Очистка предыдущего содержимого
        if group.layout():
            QWidget().setLayout(group.layout())
        
        main_layout = QVBoxLayout()
        
        # 1. Группа процессора
        cpu_group = QGroupBox("Процессор")
        cpu_layout = QFormLayout()
        
        cpu_data = state.get('CPU', {})
        if 'error' not in cpu_data:
            # Основные характеристики
            cpu_layout.addRow(QLabel("<b>Основные параметры:</b>"))
            cpu_layout.addRow("Модель:", QLabel(cpu_data.get('model', 'N/A')))
            cpu_layout.addRow("Ядер/потоков:", QLabel(f"{cpu_data.get('cores', 'N/A')}/{cpu_data.get('threads', 'N/A')}"))
            cpu_layout.addRow("Загрузка:", self._create_colored_label(cpu_data.get('usage', 0), 'percent'))
            
            # Частоты
            cpu_layout.addRow(QLabel("<b>Частоты:</b>"))
            cpu_layout.addRow("Текущая:", QLabel(f"{cpu_data.get('freq_current', 'N/A')} MHz"))
            cpu_layout.addRow("Минимальная:", QLabel(f"{cpu_data.get('freq_min', 'N/A')} MHz"))
            cpu_layout.addRow("Максимальная:", QLabel(f"{cpu_data.get('freq_max', 'N/A')} MHz"))
            
            # Температуры
            if cpu_data.get('temperatures'):
                cpu_layout.addRow(QLabel("<b>Температуры:</b>"))
                for sensor, entries in cpu_data['temperatures'].items():
                    for entry in entries:
                        temp_text = f"{entry['current']}°C (макс {entry['high']})"
                        cpu_layout.addRow(
                            f"{entry['label']}:", 
                            self._create_colored_label(entry['current'], 'temp')
                        )
        else:
            cpu_layout.addRow(QLabel(f"Ошибка: {cpu_data['error']}"))
        
        cpu_group.setLayout(cpu_layout)
        main_layout.addWidget(cpu_group)
        
        # 2. Группа памяти
        ram_group = QGroupBox("Оперативная память")
        ram_layout = QFormLayout()
        
        ram_data = state.get('RAM', {})
        if ram_data:
            ram_layout.addRow(QLabel("<b>Оперативная память:</b>"))
            ram_layout.addRow("Всего:", QLabel(f"{ram_data.get('ram', 'N/A')} ГБ"))
            ram_layout.addRow("Использовано:", self._create_colored_label(ram_data.get('percent', 0), 'percent'))
            ram_layout.addRow("Тип:", QLabel(ram_data.get('type', 'Не определен')))
            ram_layout.addRow("Скорость:", QLabel(ram_data.get('speed', 'N/A (нужен root)')))
            
            # Дополнительная информация (если есть)
            if 'type' in ram_data or 'speed' in ram_data:
                ram_layout.addRow(QLabel("<b>Характеристики:</b>"))
                if 'type' in ram_data:
                    ram_layout.addRow("Тип:", QLabel(ram_data['type']))
                if 'speed' in ram_data:
                    ram_layout.addRow("Скорость:", QLabel(f"{ram_data['speed']} МГц"))
        else:
            ram_layout.addRow(QLabel("Данные недоступны"))
        
        ram_group.setLayout(ram_layout)
        main_layout.addWidget(ram_group)
        
        # 3. Группа видеокарты
        gpu_group = QGroupBox("Видеокарта")
        gpu_layout = QFormLayout()
        
        gpu_data = state.get('GPU', {})
        if gpu_data:
            gpu_layout.addRow(QLabel("<b>Основные параметры:</b>"))
            gpu_layout.addRow("Модель:", QLabel(gpu_data.get('name', 'N/A')))
            gpu_layout.addRow("Загрузка:", self._create_colored_label(gpu_data.get('load', 0), 'percent'))
            gpu_layout.addRow("Память:", QLabel(f"{gpu_data.get('memory_used', 'N/A')}/{gpu_data.get('memory_total', 'N/A')} МБ"))
            
            gpu_layout.addRow(QLabel("<b>Температура и частоты:</b>"))
            gpu_layout.addRow("Температура:", self._create_colored_label(gpu_data.get('temperature', 0), 'temp'))
            gpu_layout.addRow("Частота ядра:", QLabel(f"{gpu_data.get('clock_core', 'N/A')} МГц"))
            gpu_layout.addRow("Частота памяти:", QLabel(f"{gpu_data.get('clock_memory', 'N/A')} МГц"))
        else:
            gpu_layout.addRow(QLabel("Данные недоступны"))
        
        gpu_group.setLayout(gpu_layout)
        main_layout.addWidget(gpu_group)
        
        # 4. Группа накопителей
        disk_group = QGroupBox("Накопители")
        disk_layout = QVBoxLayout()
        
        disk_data = state.get('HDD', {})
        if disk_data:
            if isinstance(disk_data, list):
                for disk in disk_data:
                    disk_frame = QFrame()
                    disk_frame.setFrameShape(QFrame.Shape.StyledPanel)
                    frame_layout = QFormLayout()
                    
                    frame_layout.addRow(QLabel(f"<b>{disk.get('device', 'Диск')}:</b>"))
                    frame_layout.addRow("Файловая система:", QLabel(disk.get('file_sys', 'N/A')))
                    frame_layout.addRow("Использовано:", self._create_colored_label(disk.get('percent', 0), 'percent'))
                    frame_layout.addRow("Всего:", QLabel(f"{disk.get('size', 'N/A')} ГБ"))
                    frame_layout.addRow("Свободно:", QLabel(f"{disk.get('free', 'N/A')} ГБ"))
                    
                    if 'temperature' in disk:
                        frame_layout.addRow("Температура:", self._create_colored_label(disk['temperature'], 'temp'))
                    
                    disk_frame.setLayout(frame_layout)
                    disk_layout.addWidget(disk_frame)
            else:
                frame_layout = QFormLayout()
                frame_layout.addRow(QLabel("Данные о дисках в неожиданном формате"))
                disk_layout.addLayout(frame_layout)
        else:
            disk_layout.addWidget(QLabel("Данные недоступны"))
        
        disk_group.setLayout(disk_layout)
        main_layout.addWidget(disk_group)
        
        main_layout.addStretch()
        group.setLayout(main_layout)

    def _create_colored_label(self, value, value_type):
        """Создает QLabel с цветом в зависимости от значения"""
        label = QLabel(str(value))
        
        if value_type == 'percent':
            try:
                num = float(value) if isinstance(value, (int, float)) else float(value.replace('%', ''))
            except ValueError:
                num = 0
                
            if num > 90:
                label.setStyleSheet("color: red; font-weight: bold;")
            elif num > 70:
                label.setStyleSheet("color: orange;")
            else:
                label.setStyleSheet("color: green;")
                
        elif value_type == 'temp':
            try:
                num = float(value) if isinstance(value, (int, float)) else float(value.split('°')[0])
            except (ValueError, IndexError):
                num = 0
                
            if num > 85:
                label.setStyleSheet("color: red; font-weight: bold;")
            elif num > 75:
                label.setStyleSheet("color: red;")
            elif num > 65:
                label.setStyleSheet("color: orange;")
            elif num > 50:
                label.setStyleSheet("color: yellow;")
            else:
                label.setStyleSheet("color: green;")
        
        return label

    def get_system_state(self):
        """Получение полного состояния системы с обработкой ошибок прав доступа"""
        try:
            cpu_info = get_cpu_info()
            ram_info = monitor_ram()
            gpu_info = monitor_gpu()
            hdd_info = monitor_hdd()
            
            # Дополняем данные RAM (если доступно)
            if ram_info and isinstance(ram_info, dict):
                try:
                    # Пытаемся получить информацию о памяти, но не требуем прав root
                    output = subprocess.check_output(
                        ['dmidecode', '--type', 'memory'], 
                        stderr=subprocess.DEVNULL  # Подавляем ошибки
                    ).decode('utf-8', errors='ignore')
                    
                    ram_info['type'] = next(
                        (line.split(':')[1].strip() for line in output.split('\n') 
                        if 'Type:' in line), 'Недоступно без прав root'
                    )
                    ram_info['speed'] = next(
                        (line.split(':')[1].strip().split()[0] for line in output.split('\n') 
                        if 'Speed:' in line), 'Недоступно без прав root'
                    )
                except Exception:
                    # Если не получилось - используем значения по умолчанию
                    ram_info['type'] = 'Недоступно'
                    ram_info['speed'] = 'Недоступно'
            
            # Обработка данных GPU
            gpu_data = {}
            if gpu_info and len(gpu_info) > 0:
                gpu_data = gpu_info[0]
                gpu_data['name'] = gpu_data.get('gpu', 'N/A')
            
            return {
                'CPU': cpu_info,
                'RAM': ram_info,
                'GPU': gpu_data,
                'HDD': hdd_info
            }

        except PermissionError:
            # Возвращаем данные, которые можно получить без прав root
            return {
                'CPU': get_cpu_info(),
                'RAM': monitor_ram(),
                'GPU': monitor_gpu()[0] if monitor_gpu() else {},
                'HDD': monitor_hdd()
            }
        except Exception as e:
            print(f"Ошибка получения данных системы: {str(e)}")
            return {
                'CPU': {'error': str(e)},
                'RAM': {'error': str(e)},
                'GPU': {'error': str(e)},
                'HDD': {'error': str(e)}
            }

    def update_system_status(self):
        """Обновление статуса системы"""
        if not hasattr(self, 'before_state'):
            self.before_state = self.get_system_state()
            self.update_test_results(self.before_state, self.before_group)
        
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