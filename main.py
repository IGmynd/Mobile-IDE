from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.window import Window
import sys
import io
import traceback

# Устанавливаем темный фон для всего окна (по желанию, можно убрать)
Window.clearcolor = (0.1, 0.1, 0.1, 1)

class MobileIDE(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)

        # 1. ВЕРХНЯЯ ПАНЕЛЬ (Заголовок и кнопка)
        top_bar = BoxLayout(size_hint_y=None, height='50dp', spacing=10, padding=[10, 5, 10, 5])
        
        title = Label(text="MobileIDE", font_size='20sp', bold=True)
        
        # Кнопка теперь имеет фиксированную ширину и не будет сплющиваться
        run_btn = Button(text="Запуск", size_hint_x=None, width='120dp', background_color=(0.2, 0.6, 0.2, 1))
        run_btn.bind(on_press=self.run_code)
        
        top_bar.add_widget(title)
        top_bar.add_widget(run_btn)

        # 2. РЕДАКТОР КОДА
        self.editor = TextInput(
            text='print("Hello, MobileIDE!")\n\n# Попробуй написать что-нибудь свое:\n# for i in range(5):\n#     print(f"Итерация {i}")',
            font_size='16sp',
            background_color=(0.15, 0.15, 0.15, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(1, 1, 1, 1)
        )

        # 3. ОБЛАСТЬ ВЫВОДА (только для чтения)
        self.output = TextInput(
            readonly=True, # Запрещаем редактировать вывод руками
            font_size='14sp',
            background_color=(0.05, 0.05, 0.05, 1),
            foreground_color=(0.8, 1, 0.8, 1), # Зеленоватый текст вывода
            text="Здесь появится результат..."
        )

        self.add_widget(top_bar)
        self.add_widget(self.editor)
        self.add_widget(self.output)

    def run_code(self, instance):
        code = self.editor.text
        self.output.text = "" # Очищаем прошлый вывод

        # Перехватываем стандартный вывод (то, что делает print)
        old_stdout = sys.stdout
        sys.stdout = captured_output = io.StringIO()

        try:
            # Выполняем код!
            # exec() берет строку и выполняет её как обычный Python-код
            exec(code, {})
            
            # Забираем текст, который накопился в буфере
            result = captured_output.getvalue()
            if not result:
                result = "[Код выполнен успешно, но ничего не вывел через print()]"
            self.output.text = result
            
        except Exception as e:
            # Если произошла ошибка (например, SyntaxError или ZeroDivisionError)
            # мы перехватываем её и показываем в поле вывода
            error_msg = traceback.format_exc()
            self.output.text = f"ОШИБКА:\n{error_msg}"
            
        finally:
            # Обязательно возвращаем стандартный вывод на место, 
            # иначе приложение сломается
            sys.stdout = old_stdout


class MobileIDEApp(App):
    def build(self):
        self.title = "MobileIDE"
        return MobileIDE()

if __name__ == '__main__':
    MobileIDEApp().run()