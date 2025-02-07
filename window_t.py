from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Header, Footer, Button, Label, Static
from textual.screen import Screen
from core.cpu import get_cpu_info


class MainScreen(Screen):
    """Главный экран с кнопками для перехода в разделы диагностики."""

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield Container(
            Label("Диагностика системы", id="title"),
            Vertical(
                Button("Процессор", id="cpu", variant="primary"),
                Button("Оперативная память", id="ram", variant="primary"),
                Button("Дисковая подсистема", id="disk", variant="primary"),
                Button("Видеокарта", id="gpu", variant="primary"),
                Button("Материнская плата", id="motherboard", variant="primary"),
                Button("Напряжение", id="voltage", variant="primary"),
                Button("Диагностика", id="diagnostic", variant="primary"),
                Button("Тестирование", id="testing", variant="primary"),
            ),
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.app.push_screen(event.button.id)  


class CPUInfoScreen(Screen):
    """Экран с информацией о процессоре."""

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield Container(
            Label("Информация о процессоре", id="title"),
            Static(get_cpu_info(), id="cpu_info"),
            Button("Назад", id="back", variant="error"),
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.app.pop_screen()  


class SystemDiagnosticsApp(App):
    """Основное приложение для диагностики системы на TUI."""

    CSS = """
    #title {
        text-align: center;
        margin-bottom: 1;
    }
    """

    def on_mount(self) -> None:
        self.push_screen(MainScreen())  

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cpu":
            self.push_screen(CPUInfoScreen()) 

if __name__ == "__main__":
    app = SystemDiagnosticsApp()
    app.run()
