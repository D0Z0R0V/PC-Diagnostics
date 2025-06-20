from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize, QProcess
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QWidget, QStackedWidget, QListWidget, QGridLayout, QListWidgetItem, QMenu,
    QProgressBar, QMessageBox, QGroupBox, QScrollArea, QFormLayout
)
from PyQt6.QtGui import QPixmap, QAction, QIcon

from data.model.model import DiagnosticModel
from core.cpu import get_cpu_info
from core.gpu import monitor_gpu
from core.ram import monitor_ram
from core.hdd import monitor_hdd


import sys, json, time, random, math, multiprocessing


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
        
    def create_diagnostic_screen(self, title, description, image_path=None):
        """Создаем экран диагностики (заменяет заглушку)"""
        screen = QWidget()
        layout = QVBoxLayout(screen)
        
        # Стили
        self.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                border: 1px solid gray;
                border-radius: 5px;
                margin-top: 10px;
            }
            QLabel { font-size: 13px; }
        """)
        
        # Кнопка запуска
        self.diagnose_btn = QPushButton("Запустить диагностику")
        self.diagnose_btn.setFixedHeight(40)
        self.diagnose_btn.clicked.connect(self.start_diagnosis)
        layout.addWidget(self.diagnose_btn)
        
        # Прогресс-бар
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Группа для результатов
        self.results_group = QGroupBox("Результаты диагностики")
        results_layout = QVBoxLayout()
        
        self.results_label = QLabel("Диагностика не проводилась")
        self.results_label.setWordWrap(True)
        results_layout.addWidget(self.results_label)
        
        self.verdict_label = QLabel()
        self.verdict_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        results_layout.addWidget(self.verdict_label)
        
        self.results_group.setLayout(results_layout)
        layout.addWidget(self.results_group)
        
        # Инициализация модели
        self.diagnostic_model = DiagnosticModel()
        
        return screen

    def start_diagnosis(self):
        """Запуск диагностики в отдельном потоке"""
        self.diagnose_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.results_label.setText("Идет диагностика...")
        
        self.diagnostic_thread = DiagnosticThread(self.diagnostic_model)
        self.diagnostic_thread.update_signal.connect(self.update_progress)
        self.diagnostic_thread.finished_signal.connect(self.show_results)
        self.diagnostic_thread.start()

    def update_progress(self, value, message):
        """Обновление прогресс-бара"""
        self.progress_bar.setValue(value)
        self.progress_bar.setFormat(f"{message} {value}%")

    def show_results(self, data, verdict):
        """Показ результатов диагностики"""
        self.diagnose_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        # Формируем текст с результатами
        result_text = ""
        if data:
            cpu = data['CPU']
            gpu = data['GPU'][0] if data['GPU'] else {}
            ram = data['RAM']
            hdd = data['HDD']
            
            result_text = f"""
            <b>Процессор:</b><br>
            - Загрузка: {cpu.get('usage', 'N/A')}%<br>
            - Температура: {cpu.get('temperatures', {}).get('coretemp', [{}])[0].get('current', 'N/A')}°C<br><br>
            
            <b>Видеокарта:</b><br>
            - Загрузка: {gpu.get('load', 'N/A')}%<br>
            - Температура: {gpu.get('temperature', 'N/A')}°C<br><br>
            
            <b>Память:</b><br>
            - Использовано: {ram.get('percent', 'N/A')}%<br>
            - Доступно: {ram.get('free', 'N/A')} ГБ<br><br>
            
            <b>Диск:</b><br>
            - Использовано: {hdd.get('percent', 'N/A')}%<br>
            """
        
        self.results_label.setText(result_text)
        
        # Устанавливаем вердикт с цветом
        color = "#2ECC71" if verdict == "Normal" else "#F39C12" if verdict == "Warning" else "#E74C3C"
        self.verdict_label.setText(f"<span style='color: {color}; font-size: 18px;'>Статус: {verdict}</span>")
            
    
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
            if self.test_process.state() == QProcess.ProcessState.Running:
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
        self.test_timer.timeout.connect(lambda: self.update_progress(test_type))
        self.test_timer.start(1000)

    def update_progress(self, test_type):
        """Обновление прогресса"""
        self.test_time += 1
        progress = min(100, int((self.test_time / 60) * 100))
        self.test_progress.setValue(progress)
        
        if self.test_time >= 60:
            self.test_timer.stop()
            if self.test_process.state() == QProcess.ProcessState.Running:
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
            if value > 90:
                label.setStyleSheet("color: red; font-weight: bold;")
            elif value > 70:
                label.setStyleSheet("color: orange;")
            else:
                label.setStyleSheet("color: green;")
        elif value_type == 'temp':
            if value > 80:
                label.setStyleSheet("color: red; font-weight: bold;")
            elif value > 60:
                label.setStyleSheet("color: orange;")
            else:
                label.setStyleSheet("color: green;")
        
        return label

    def get_system_state(self):
        """Получение полного состояния системы"""
        try:
            cpu_info = get_cpu_info()
            ram_info = monitor_ram()
            gpu_info = monitor_gpu()
            hdd_info = monitor_hdd()
            
            # Дополняем данные RAM
            if ram_info and isinstance(ram_info, dict):
                try:
                    output = subprocess.check_output(['dmidecode', '--type', 'memory']).decode('utf-8')
                    ram_info['type'] = next((line.split(':')[1].strip() for line in output.split('\n') if 'Type:' in line), 'Unknown')
                    ram_info['speed'] = next((line.split(':')[1].strip().split()[0] for line in output.split('\n') if 'Speed:' in line), 'Unknown')
                except:
                    ram_info['type'] = 'N/A'
                    ram_info['speed'] = 'N/A'
            
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
        except Exception as e:
            print(f"Ошибка получения данных системы: {str(e)}")
            return {
                'CPU': {'error': str(e)},
                'RAM': {},
                'GPU': {},
                'HDD': {}
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



