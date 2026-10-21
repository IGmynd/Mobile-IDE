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
from kivy.clock import Clock
import sys
import io
import traceback
import os
import threading

THEME_COLOR = (0.6, 0.2, 0.8, 1)
MENU_BG_COLOR = (0.3, 0.1, 0.4, 1)

Window.clearcolor = THEME_COLOR
Window.softinput_mode = 'below_target'

class MainLayout(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.menu_left_open = False
        self.menu_right_open = False
        self.current_file = "main_script.py"
        self.is_running = False # Флаг для защиты от зависаний

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

        # Редактор (теперь в ScrollView, чтобы не ломался при маленьком экране)
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

        # ПАНЕЛЬ БЫСТРЫХ СИМВОЛОВ (Над клавиатурой/редактором)
        self.shortcut_bar = BoxLayout(size_hint_y=None, height='40dp', spacing=2)
        self.shortcut_bar.canvas.before.add(Color(0.2, 0.2, 0.2, 1))
        self.shortcut_bar.canvas.before.add(Rectangle(size=self.shortcut_bar.size, pos=self.shortcut_bar.pos))
        self.shortcut_bar.bind(size=self._update_shortcut_bg, pos=self._update_shortcut_bg)
        
        shortcuts = ["Tab", ":", "=", "(", ")", "[", "]", "{", "}", '"', "'", "+", "-"]
        for sym in shortcuts:
            btn = Button(text=sym, font_size='12sp', background_color=(0.3, 0.3, 0.3, 1))
            # Используем лямбду, чтобы передать конкретный символ
            btn.bind(on_press=lambda x, s=sym: self.insert_shortcut(s))
            self.shortcut_bar.add_widget(btn)

        self.main_content.add_widget(self.top_bar)
        self.main_content.add_widget(self.editor)
        self.main_content.add_widget(self.shortcut_bar) # Панель символов
        self.main_content.add_widget(self.output)

        # === ЛЕВОЕ МЕНЮ ===
        self.side_menu_left = BoxLayout(orientation='vertical', size_hint=(None, 1), width='220dp', pos_hint={'x': -1}, padding=10, spacing=10)
        with self.side_menu_left.canvas.before:
            Color(*MENU_BG_COLOR)
            self.menu_left_bg = Rectangle(size=self.side_menu_left.size, pos=self.side_menu_left.pos)
        self.side_menu_left.bind(size=self._update_left_bg, pos=self._update_left_bg)

        btn_save = Button(text="Сохранить", size_hint_y=None, height='50dp', background_color=(0.2, 0.4, 0.8, 1))
        btn_save.bind(on_press=self.save_code)
        btn_clear = Button(text="Очистить", size_hint_y=None, height='50dp', background_color=(0.5, 0.5, 0.5, 1))
        btn_clear.bind(on_press=self.clear_all)
        
        self.btn_run = Button(text="Запуск", size_hint_y=None, height='50dp', background_color=(0.2, 0.6, 0.2, 1))
        self.btn_run.bind(on_press=self.run_code)

        self.side_menu_left.add_widget(Label(text="Действия", size_hint_y=None, height='40dp', bold=True))
        self.side_menu_left.add_widget(btn_save)
        self.side_menu_left.add_widget(btn_clear)
        self.side_menu_left.add_widget(self.btn_run)
        self.side_menu_left.add_widget(Label())

        # === ПРАВОЕ МЕНЮ ===
        self.side_menu_right = BoxLayout(orientation='vertical', size_hint=(None, 1), width='260dp', pos_hint={'x': 1}, padding=10, spacing=10)
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
    def _update_shortcut_bg(self, instance, value):
        instance.canvas.before.clear()
        with instance.canvas.before:
            Color(0.2, 0.2, 0.2, 1)
            Rectangle(size=instance.size, pos=instance.pos)

    # --- Быстрые символы ---
    def insert_shortcut(self, text):
        if not self.editor.focus:
            self.editor.focus = True
        
        # Если нажали Tab, вставляем 4 пробела
        if text == "Tab":
            self.editor.insert_text("    ")
        else:
            self.editor.insert_text(text)

    # --- Анимация меню ---
    def toggle_left_menu(self, instance=None):
        if self.menu_right_open: self.toggle_right_menu()
        anim = Animation(pos_hint={'x': -1 if self.menu_left_open else 0}, duration=0.2)
        anim.start(self.side_menu_left)
        self.menu_left_open = not self.menu_left_open

    def toggle_right_menu(self, instance=None):
        if self.menu_left_open: self.toggle_left_menu()
        target_x = 1 if self.menu_right_open else 1 - (self.side_menu_right.width / Window.width)
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
            # Создаем горизонтальный контейнер для файла и кнопки удаления
            row = BoxLayout(size_hint_y=None, height='45dp', spacing=2)
            
            bg_color = (0.4, 0.2, 0.5, 1) if filename == self.current_file else (0.2, 0.2, 0.2, 0.8)
            btn = Button(text=filename, background_color=bg_color, halign='left')
            btn.bind(on_press=lambda x, fn=filename: self.load_file(fn))
            
            # Кнопка удаления
            del_btn = Button(text="✕", size_hint_x=None, width='40dp', background_color=(0.8, 0.2, 0.2, 1))
            del_btn.bind(on_press=lambda x, fn=filename: self.delete_file(fn))

            row.add_widget(btn)
            row.add_widget(del_btn)
            self.files_layout.add_widget(row)

    def load_file(self, filename):
        filepath = os.path.join(self.projects_dir, filename)
        if os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    self.editor.text = f.read()
                self.current_file = filename
                self.output.text = f"Открыт файл: {filename}"
                self.refresh_files()
                if self.menu_right_open: self.toggle_right_menu()
            except Exception as e:
                self.output.text = f"Ошибка чтения: {e}"

    def delete_file(self, filename):
        if filename == "main_script.py":
            self.output.text = "❌ Нельзя удалить системный файл main_script.py"
            return
        filepath = os.path.join(self.projects_dir, filename)
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
                if self.current_file == filename:
                    self.load_file("main_script.py")
                else:
                    self.refresh_files()
                self.output.text = f"Файл {filename} удален."
            except Exception as e:
                self.output.text = f"Ошибка удаления: {e}"

    def save_code(self, instance):
        filepath = os.path.join(self.projects_dir, self.current_file)
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(self.editor.text)
            self.output.text = f"Сохранено: {self.current_file}"
        except Exception as e:
            self.output.text = f"Ошибка сохранения: {e}"
        if self.menu_left_open: self.toggle_left_menu()

    def show_new_file_popup(self, instance):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        text_input = TextInput(text="script", multiline=False, size_hint_y=None, height='40dp')
        btn_layout = BoxLayout(size_hint_y=None, height='40dp', spacing=10)
        btn_cancel = Button(text="Отмена", background_color=(0.6, 0.2, 0.2, 1))
        btn_create = Button(text="Создать", background_color=(0.2, 0.6, 0.2, 1))

        btn_layout.add_widget(btn_cancel)
        btn_layout.add_widget(btn_create)
        content.add_widget(Label(text="Имя файла:", size_hint_y=None, height='30dp'))
        content.add_widget(text_input)
        content.add_widget(btn_layout)

        popup = Popup(title="Новый файл", content=content, size_hint=(0.85, 0.4))

        def create_action(instance):
            name = text_input.text.strip()
            if name:
                filename = f"{name}.py" if not name.endswith('.py') else name
                filepath = os.path.join(self.projects_dir, filename)
                if not os.path.exists(filepath):
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(f'# Файл {filename}\n')
                    self.load_file(filename)
                popup.dismiss()

        btn_cancel.bind(on_press=popup.dismiss)
        btn_create.bind(on_press=create_action)
        popup.open()
        text_input.focus = True

    def clear_all(self, instance):
        self.output.text = ""
        if self.menu_left_open: self.toggle_left_menu()

    # --- Запуск кода (В ОТДЕЛЬНОМ ПОТОКЕ) ---
    def run_code(self, instance):
        if self.is_running:
            self.output.text = "Код уже выполняется... Подожди или нажми Стоп."
            return

        code = self.editor.text
        self.output.text = "Выполняется..."
        self.is_running = True
        
        # Меняем кнопку на красную "Стоп" (пока просто меняем текст, логику стопа добавим позже)
        self.btn_run.text = "Выполняется..."
        self.btn_run.background_color = (0.8, 0.2, 0.2, 1)

        if self.menu_left_open: self.toggle_left_menu()

        # Запускаем в фоновом потоке, чтобы не вешать интерфейс
        thread = threading.Thread(target=self._execute_code_in_thread, args=(code,))
        thread.daemon = True
        thread.start()

    def _execute_code_in_thread(self, code):
        old_stdout = sys.stdout
        sys.stdout = captured_output = io.StringIO()
        
        try:
            # Выполняем код
            exec(code, {})
            result = captured_output.getvalue()
            if not result:
                result = "[Код выполнен успешно]"
        except Exception:
            result = f"ОШИБКА:\n{traceback.format_exc()}"
        finally:
            sys.stdout = old_stdout
            # Возвращаемся в главный поток и обновляем интерфейс через Clock (это требование Kivy)
            Clock.schedule_once(lambda dt: self._finish_execution(result))

    def _finish_execution(self, result):
        self.output.text = result
        self.is_running = False
        self.btn_run.text = "Запуск"
        self.btn_run.background_color = (0.2, 0.6, 0.2, 1)


class MobileIDEApp(App):
    def build(self):
        self.title = "MobileIDE"
        return MainLayout()

if __name__ == '__main__':
    MobileIDEApp().run()