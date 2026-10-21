from kivy.config import Config
Config.set('graphics', 'orientation', 'portrait')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.animation import Animation
from kivy.graphics import Color, Rectangle
import sys
import io
import traceback
import os

# Твой цвет #9933cc в формате Kivy RGBA
THEME_COLOR = (0.6, 0.2, 0.8, 1)
MENU_BG_COLOR = (0.3, 0.1, 0.4, 1) # Темно-фиолетовый для панелей

Window.clearcolor = THEME_COLOR

# МАГИЯ ДЛЯ КЛАВИАТУРЫ: сдвигает интерфейс вверх, чтобы поле ввода не перекрывалось
Window.softinput_mode = 'below_target'

class MainLayout(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.menu_left_open = False
        self.menu_right_open = False
        self.current_file = "main_script.py"

        # Путь к папке с проектами
        app = App.get_running_app()
        self.projects_dir = os.path.join(app.user_data_dir, "projects")
        if not os.path.exists(self.projects_dir):
            os.makedirs(self.projects_dir)

        # === ОСНОВНОЙ КОНТЕНТ ===
        self.main_content = BoxLayout(orientation='vertical')
        
        # Верхняя панель
        self.top_bar = BoxLayout(size_hint_y=None, height='50dp', spacing=5, padding=[5, 5, 5, 5])
        
        with self.top_bar.canvas.before:
            Color(*THEME_COLOR)
            self.top_bar_bg = Rectangle(size=self.top_bar.size, pos=self.top_bar.pos)
        self.top_bar.bind(size=self._update_top_bar_bg, pos=self._update_top_bar_bg)
        
        self.menu_left_btn = Button(text="Меню", size_hint_x=None, width='80dp', font_size='14sp', background_color=MENU_BG_COLOR)
        self.menu_left_btn.bind(on_press=self.toggle_left_menu)
        
        title = Label(text="MobileIDE", font_size='18sp', bold=True)
        
        self.menu_right_btn = Button(text="Файлы", size_hint_x=None, width='80dp', font_size='14sp', background_color=MENU_BG_COLOR)
        self.menu_right_btn.bind(on_press=self.toggle_right_menu)

        self.top_bar.add_widget(self.menu_left_btn)
        self.top_bar.add_widget(title)
        self.top_bar.add_widget(self.menu_right_btn)

        # Редактор
        self.editor = TextInput(
            text='print("Hello, MobileIDE!")\n',
            font_size='16sp',
            background_color=(0.12, 0.12, 0.12, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(1, 1, 1, 1)
        )

        # Вывод
        self.output = TextInput(
            readonly=True,
            font_size='14sp',
            background_color=(0.08, 0.08, 0.08, 1),
            foreground_color=(0.8, 1, 0.8, 1),
            text="Готов к работе..."
        )

        self.main_content.add_widget(self.top_bar)
        self.main_content.add_widget(self.editor)
        self.main_content.add_widget(self.output)

        # === ЛЕВОЕ МЕНЮ (Действия) ===
        self.side_menu_left = BoxLayout(
            orientation='vertical', 
            size_hint=(None, 1), 
            width='220dp', 
            pos_hint={'x': -1}, 
            padding=10, 
            spacing=10
        )
        with self.side_menu_left.canvas.before:
            Color(*MENU_BG_COLOR)
            self.menu_left_bg = Rectangle(size=self.side_menu_left.size, pos=self.side_menu_left.pos)
        self.side_menu_left.bind(size=self._update_left_bg, pos=self._update_left_bg)

        btn_save = Button(text="Сохранить", size_hint_y=None, height='50dp', background_color=(0.2, 0.4, 0.8, 1))
        btn_save.bind(on_press=self.save_code)
        btn_clear = Button(text="Очистить", size_hint_y=None, height='50dp', background_color=(0.5, 0.5, 0.5, 1))
        btn_clear.bind(on_press=self.clear_all)
        btn_run = Button(text="Запуск", size_hint_y=None, height='50dp', background_color=(0.2, 0.6, 0.2, 1))
        btn_run.bind(on_press=self.run_code)

        self.side_menu_left.add_widget(Label(text="Действия", size_hint_y=None, height='40dp', bold=True))
        self.side_menu_left.add_widget(btn_save)
        self.side_menu_left.add_widget(btn_clear)
        self.side_menu_left.add_widget(btn_run)
        self.side_menu_left.add_widget(Label())

        # === ПРАВОЕ МЕНЮ (Файлы) ===
        self.side_menu_right = BoxLayout(
            orientation='vertical', 
            size_hint=(None, 1), 
            width='250dp', 
            pos_hint={'x': 1}, 
            padding=10, 
            spacing=10
        )
        with self.side_menu_right.canvas.before:
            Color(*MENU_BG_COLOR)
            self.menu_right_bg = Rectangle(size=self.side_menu_right.size, pos=self.side_menu_right.pos)
        self.side_menu_right.bind(size=self._update_right_bg, pos=self._update_right_bg)

        header_layout = BoxLayout(size_hint_y=None, height='40dp')
        header_layout.add_widget(Label(text="Проекты", bold=True, halign='left'))
        new_file_btn = Button(text="+ Файл", size_hint_x=None, width='80dp', background_color=(0.2, 0.6, 0.2, 1))
        new_file_btn.bind(on_press=self.show_new_file_popup)
        header_layout.add_widget(new_file_btn)
        self.side_menu_right.add_widget(header_layout)

        self.files_scroll = ScrollView()
        self.files_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=5)
        self.files_layout.bind(minimum_height=self.files_layout.setter('height'))
        self.files_scroll.add_widget(self.files_layout)
        self.side_menu_right.add_widget(self.files_scroll)

        # Добавляем всё на экран
        self.add_widget(self.main_content)
        self.add_widget(self.side_menu_left)
        self.add_widget(self.side_menu_right)

        self.refresh_files()
        self.load_file(self.current_file)

    # --- Обновление фонов ---
    def _update_top_bar_bg(self, instance, value):
        self.top_bar_bg.pos = instance.pos
        self.top_bar_bg.size = instance.size
    def _update_left_bg(self, instance, value):
        self.menu_left_bg.pos = instance.pos
        self.menu_left_bg.size = instance.size
    def _update_right_bg(self, instance, value):
        self.menu_right_bg.pos = instance.pos
        self.menu_right_bg.size = instance.size

    # --- Анимация меню ---
    def toggle_left_menu(self, instance=None):
        if self.menu_right_open:
            self.toggle_right_menu()

        if self.menu_left_open:
            anim = Animation(pos_hint={'x': -1}, duration=0.2)
        else:
            anim = Animation(pos_hint={'x': 0}, duration=0.2)
        anim.start(self.side_menu_left)
        self.menu_left_open = not self.menu_left_open

    def toggle_right_menu(self, instance=None):
        if self.menu_left_open:
            self.toggle_left_menu()

        if self.menu_right_open:
            anim = Animation(pos_hint={'x': 1}, duration=0.2)
        else:
            target_x = 1 - (self.side_menu_right.width / Window.width)
            anim = Animation(pos_hint={'x': target_x}, duration=0.2)
        anim.start(self.side_menu_right)
        self.menu_right_open = not self.menu_right_open

    # --- Работа с файлами ---
    def refresh_files(self):
        self.files_layout.clear_widgets()
        files = [f for f in os.listdir(self.projects_dir) if f.endswith('.py')]
        
        if not files:
            with open(os.path.join(self.projects_dir, "main_script.py"), "w") as f:
                f.write('print("Hello, MobileIDE!")\n')
            files = ["main_script.py"]

        for filename in files:
            bg_color = (0.4, 0.2, 0.5, 1) if filename == self.current_file else (0.2, 0.2, 0.2, 0.8)
            btn = Button(text=filename, size_hint_y=None, height='45dp', background_color=bg_color, halign='left')
            btn.bind(on_press=lambda x, fn=filename: self.load_file(fn))
            self.files_layout.add_widget(btn)

    def load_file(self, filename):
        filepath = os.path.join(self.projects_dir, filename)
        if os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    self.editor.text = f.read()
                self.current_file = filename
                self.output.text = f"Открыт файл: {filename}"
                self.refresh_files()
                if self.menu_right_open:
                    self.toggle_right_menu()
            except Exception as e:
                self.output.text = f"Ошибка чтения: {e}"

    def save_code(self, instance):
        filepath = os.path.join(self.projects_dir, self.current_file)
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(self.editor.text)
            self.output.text = f"Сохранено: {self.current_file}"
        except Exception as e:
            self.output.text = f"Ошибка сохранения: {e}"
        if self.menu_left_open:
            self.toggle_left_menu()

    def show_new_file_popup(self, instance):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        popup_label = Label(text="Имя файла (без .py):", size_hint_y=None, height='30dp')
        
        # Текстовое поле
        text_input = TextInput(text="script", multiline=False, size_hint_y=None, height='40dp')
        
        btn_layout = BoxLayout(size_hint_y=None, height='40dp', spacing=10)
        btn_cancel = Button(text="Отмена", background_color=(0.6, 0.2, 0.2, 1))
        btn_create = Button(text="Создать", background_color=(0.2, 0.6, 0.2, 1))

        btn_layout.add_widget(btn_cancel)
        btn_layout.add_widget(btn_create)

        content.add_widget(popup_label)
        content.add_widget(text_input)
        content.add_widget(btn_layout)

        # Уменьшили высоту окна (0.4), чтобы оно точно поместилось над клавиатурой
        popup = Popup(title="Новый файл", content=content, size_hint=(0.85, 0.4), auto_dismiss=False)

        def create_action(instance):
            name = text_input.text.strip()
            if name:
                filename = f"{name}.py" if not name.endswith('.py') else name
                filepath = os.path.join(self.projects_dir, filename)
                if not os.path.exists(filepath):
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(f'# Файл {filename}\nprint("Привет из {filename}")\n')
                    self.load_file(filename)
                popup.dismiss()

        btn_cancel.bind(on_press=popup.dismiss)
        btn_create.bind(on_press=create_action)
        
        # Открываем окно и сразу ставим фокус на поле ввода, 
        # чтобы клавиатура выехала моментально
        popup.open()
        text_input.focus = True

    def clear_all(self, instance):
        self.output.text = ""
        self.editor.text = ""
        if self.menu_left_open:
            self.toggle_left_menu()

    # --- Запуск кода ---
    def run_code(self, instance):
        code = self.editor.text
        self.output.text = ""

        old_stdout = sys.stdout
        sys.stdout = captured_output = io.StringIO()

        try:
            exec(code, {})
            result = captured_output.getvalue()
            if not result:
                result = "[Код выполнен успешно]"
            self.output.text = result
        except Exception:
            error_msg = traceback.format_exc()
            self.output.text = f"ОШИБКА:\n{error_msg}"
        finally:
            sys.stdout = old_stdout
        if self.menu_left_open:
            self.toggle_left_menu()

class MobileIDEApp(App):
    def build(self):
        self.title = "MobileIDE"
        return MainLayout()

if __name__ == '__main__':
    MobileIDEApp().run()