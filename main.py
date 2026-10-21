from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.window import Window
import sys
import io
import traceback
import os

Window.clearcolor = (0.1, 0.1, 0.1, 1)

class MobileIDE(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)

        # 1. ВЕРХНЯЯ ПАНЕЛЬ
        top_bar = BoxLayout(size_hint_y=None, height='50dp', spacing=5, padding=[5, 5, 5, 5])
        
        title = Label(text="MobileIDE", font_size='18sp', bold=True, size_hint_x=0.4)
        
        save_btn = Button(text="Сохранить", size_hint_x=None, width='90dp', background_color=(0.2, 0.4, 0.8, 1))
        save_btn.bind(on_press=self.save_code)
        
        clear_btn = Button(text="Очистить", size_hint_x=None, width='90dp', background_color=(0.5, 0.5, 0.5, 1))
        clear_btn.bind(on_press=self.clear_all)
        
        run_btn = Button(text="Запуск", size_hint_x=None, width='90dp', background_color=(0.2, 0.6, 0.2, 1))
        run_btn.bind(on_press=self.run_code)
        
        top_bar.add_widget(title)
        top_bar.add_widget(save_btn)
        top_bar.add_widget(clear_btn)
        top_bar.add_widget(run_btn)

        # 2. РЕДАКТОР
        self.editor = TextInput(
            text='print("Hello, MobileIDE!")\n\n# Попробуй написать что-нибудь свое:\n# for i in range(5):\n#     print(f"Итерация {i}")',
            font_size='16sp',
            background_color=(0.15, 0.15, 0.15, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(1, 1, 1, 1)
        )

        # 3. ВЫВОД
        self.output = TextInput(
            readonly=True,
            font_size='14sp',
            background_color=(0.05, 0.05, 0.05, 1),
            foreground_color=(0.8, 1, 0.8, 1),
            text="Здесь появится результат..."
        )

        self.add_widget(top_bar)
        self.add_widget(self.editor)
        self.add_widget(self.output)

    def clear_all(self, instance):
        self.output.text = ""
        self.editor.text = ""

    def save_code(self, instance):
        # Получаем путь к папке, где Android разрешает приложению хранить файлы
        app = App.get_running_app()
        file_path = os.path.join(app.user_data_dir, "main_script.py")
        
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(self.editor.text)
            self.output.text = f"✅ Код успешно сохранен!\nПуть: {file_path}"
        except Exception as e:
            self.output.text = f"❌ Ошибка сохранения: {e}"

    def run_code(self, instance):
        code = self.editor.text
        self.output.text = ""

        old_stdout = sys.stdout
        sys.stdout = captured_output = io.StringIO()

        try:
            exec(code, {})
            result = captured_output.getvalue()
            if not result:
                result = "[Код выполнен успешно, но ничего не вывел через print()]"
            self.output.text = result
        except Exception:
            error_msg = traceback.format_exc()
            self.output.text = f"ОШИБКА:\n{error_msg}"
        finally:
            sys.stdout = old_stdout


class MobileIDEApp(App):
    def build(self):
        self.title = "MobileIDE"
        return MobileIDE()

    def on_start(self):
        # При запуске приложения проверяем, есть ли сохраненный файл
        file_path = os.path.join(self.user_data_dir, "main_script.py")
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    # Находим наш редактор по id или по дереву виджетов
                    # Так как у нас один корневой виджет, просто обращаемся к нему
                    self.root.editor.text = content
                    self.root.output.text = "Файл main_script.py загружен."
            except Exception as e:
                self.root.output.text = f"Ошибка загрузки файла: {e}"

if __name__ == '__main__':
    MobileIDEApp().run()