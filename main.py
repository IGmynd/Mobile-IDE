
from kivy.config import Config
# Принудительно включаем вертикальную (портретную) ориентацию
Config.set('graphics', 'orientation', 'portrait')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.animation import Animation
from kivy.graphics import Color, Rectangle
import sys
import io
import traceback
import os

Window.clearcolor = (0.1, 0.1, 0.1, 1)

class MainLayout(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.menu_open = False

        # === ОСНОВНОЙ КОНТЕНТ ===
        self.main_content = BoxLayout(orientation='vertical')
        
        # Верхняя панель (только заголовок и меню)
        top_bar = BoxLayout(size_hint_y=None, height='50dp', spacing=5, padding=[5, 5, 5, 5])
        
        self.menu_btn = Button(text="☰", size_hint_x=None, width='50dp', font_size='24sp', background_color=(0.2, 0.2, 0.2, 1))
        self.menu_btn.bind(on_press=self.toggle_menu)
        
        title = Label(text="MobileIDE", font_size='18sp', bold=True)
        
        top_bar.add_widget(self.menu_btn)
        top_bar.add_widget(title)

        # Редактор
        self.editor = TextInput(
            text='print("Hello, MobileIDE!")\n\n# Попробуй написать что-нибудь свое:\n# for i in range(5):\n#     print(f"Итерация {i}")',
            font_size='16sp',
            background_color=(0.15, 0.15, 0.15, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(1, 1, 1, 1)
        )

        # Вывод
        self.output = TextInput(
            readonly=True,
            font_size='14sp',
            background_color=(0.05, 0.05, 0.05, 1),
            foreground_color=(0.8, 1, 0.8, 1),
            text="Здесь появится результат..."
        )

        self.main_content.add_widget(top_bar)
        self.main_content.add_widget(self.editor)
        self.main_content.add_widget(self.output)

        # === ВЫДВИЖНОЕ МЕНЮ СЛЕВА ===
        self.side_menu = BoxLayout(
            orientation='vertical', 
            size_hint=(None, 1), 
            width='220dp', 
            pos_hint={'x': -1}, # Изначально спрятано за левым краем экрана
            padding=10, 
            spacing=10
        )
        
        # Задний фон для меню, чтобы редактор не просвечивал
        with self.side_menu.canvas.before:
            Color(0.2, 0.2, 0.2, 1)
            self.menu_bg = Rectangle(size=self.side_menu.size, pos=self.side_menu.pos)
        self.side_menu.bind(size=self._update_rect, pos=self._update_rect)

        # Кнопки внутри меню
        btn_save = Button(text="Сохранить", size_hint_y=None, height='50dp', background_color=(0.2, 0.4, 0.8, 1))
        btn_save.bind(on_press=self.save_code)
        
        btn_clear = Button(text="Очистить", size_hint_y=None, height='50dp', background_color=(0.5, 0.5, 0.5, 1))
        btn_clear.bind(on_press=self.clear_all)
        
        btn_run = Button(text="Запуск", size_hint_y=None, height='50dp', background_color=(0.2, 0.6, 0.2, 1))
        btn_run.bind(on_press=self.run_code)

        self.side_menu.add_widget(Label(text="Действия", size_hint_y=None, height='40dp', bold=True))
        self.side_menu.add_widget(btn_save)
        self.side_menu.add_widget(btn_clear)
        self.side_menu.add_widget(btn_run)
        self.side_menu.add_widget(Label()) # Пружина, чтобы кнопки были сверху

        # Добавляем всё на экран
        self.add_widget(self.main_content)
        self.add_widget(self.side_menu)

    def _update_rect(self, instance, value):
        self.menu_bg.pos = instance.pos
        self.menu_bg.size = instance.size

    def toggle_menu(self, instance=None):
        if self.menu_open:
            # Закрыть (уехать влево за экран)
            anim = Animation(pos_hint={'x': -1}, duration=0.2)
        else:
            # Открыть (выехать на экран)
            anim = Animation(pos_hint={'x': 0}, duration=0.2)
        
        anim.start(self.side_menu)
        self.menu_open = not self.menu_open

    def clear_all(self, instance):
        self.output.text = ""
        self.editor.text = ""
        self.toggle_menu() # Закрываем меню после действия

    def save_code(self, instance):
        app = App.get_running_app()
        file_path = os.path.join(app.user_data_dir, "main_script.py")
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(self.editor.text)
            self.output.text = f"✅ Код сохранен!\nПуть: {file_path}"
        except Exception as e:
            self.output.text = f"❌ Ошибка сохранения: {e}"
        self.toggle_menu()

    def run_code(self, instance):
        code = self.editor.text
        self.output.text = ""

        old_stdout = sys.stdout
        sys.stdout = captured_output = io.StringIO()

        try:
            exec(code, {})
            result = captured_output.getvalue()
            if not result:
                result = "[Код выполнен успешно, но ничего не вывел]"
            self.output.text = result
        except Exception:
            error_msg = traceback.format_exc()
            self.output.text = f"ОШИБКА:\n{error_msg}"
        finally:
            sys.stdout = old_stdout
        self.toggle_menu() # Закрываем меню после действия


class MobileIDEApp(App):
    def build(self):
        self.title = "MobileIDE"
        return MainLayout()

    def on_start(self):
        file_path = os.path.join(self.user_data_dir, "main_script.py")
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    self.root.editor.text = content
                    self.root.output.text = "Файл main_script.py загружен."
            except Exception as e:
                self.root.output.text = f"Ошибка загрузки: {e}"

if __name__ == '__main__':
    MobileIDEApp().run()