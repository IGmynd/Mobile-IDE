from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput


class MobileIDE(App):
    def build(self):
        self.title = "MobileIDE"

        root = BoxLayout(
            orientation="vertical",
            padding=8,
            spacing=8,
        )

        header = BoxLayout(
            size_hint_y=None,
            height=48,
            spacing=8,
        )

        title = Label(
            text="MobileIDE",
            font_size="22sp",
        )

        run_button = Button(
            text="Запуск",
            size_hint_x=None,
            width=100,
        )
        run_button.bind(on_press=self.run_code)

        header.add_widget(title)
        header.add_widget(run_button)

        self.editor = TextInput(
            text='print("Hello, MobileIDE!")\n',
            multiline=True,
            font_size="16sp",
            size_hint_y=0.65,
        )

        self.output = TextInput(
            text="Вывод программы появится здесь.",
            readonly=True,
            multiline=True,
            font_size="14sp",
            size_hint_y=0.35,
        )

        root.add_widget(header)
        root.add_widget(self.editor)
        root.add_widget(self.output)

        return root

    def run_code(self, instance):
        self.output.text = (
            "Запуск Python-кода будет реализован следующим этапом."
        )


if __name__ == "__main__":
    MobileIDE().run()