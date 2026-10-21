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
import shutil

from plyer import filechooser

# --- ЦВЕТОВАЯ ПАЛИТРА ---
THEME_COLOR = (0.878, 0.690, 1, 1)      # #e0b0ff (Фон)
MENU_BG_COLOR = (0.878, 0.690, 1, 1)    # #e0b0ff (Фон меню)
BTN_DEFAULT = (0, 0.184, 0.333, 1)      # #002f55 (Синий)
BTN_RUN = (0.329, 1, 0.623, 1)          # #54ff9f (Зеленый)
BTN_DELETE = (0.972, 0.090, 0.243, 1)   # #f8173e (Красный)
TEXT_WHITE = (1, 1, 1, 1)
TEXT_BLACK = (0, 0, 0, 1)

Window.clearcolor = THEME_COLOR

class CodeEditor(TextInput):
    def insert_text(self, substring, from_undo=False):
        if substring == '\n':
            lines = self.text.split('\n')
            current_line = lines[-1] if lines else ""
            if current_line.strip().endswith(':'):
                substring = '\n    '
            elif current_line.startswith('    '):
                indent = len(current_line) - len(current_line.lstrip())
                substring = '\n' + (' ' * indent)
        super().insert_text(substring, from_undo)

class MainLayout(FloatLayout):
    def __init__(self, projects_dir, **kwargs):
        super().__init__(**kwargs)
        self.projects_dir = projects_dir
        self.menu_left_open = False
        self.menu_right_open = False
        self.current_file = "main_script.py"
        self.is_large_font = False
        self.output_hidden = False

        # === ОСНОВНОЙ КОНТЕНТ ===
        self.main_content = BoxLayout(orientation='vertical')
        
        self.top_bar = BoxLayout(size_hint_y=None, height='50dp', spacing=5, padding=[5, 5, 5, 5])
        with self.top_bar.canvas.before:
            Color(*THEME_COLOR)
            self.top_bar_bg = Rectangle(size=self.top_bar.size, pos=self.top_bar.pos)
        self.top_bar.bind(size=self._update_top_bar_bg, pos=self._update_top_bar_bg)
        
        self.menu_left_btn = Button(text="Меню", size_hint_x=None, width='80dp', font_size='14sp', background_color=BTN_DEFAULT)
        self.menu_left_btn.bind(on_press=self.toggle_left_menu)
        title = Label(text="MobileIDE", font_size='18sp', bold=True, color=TEXT_BLACK)
        self.menu_right_btn = Button(text="Файлы", size_hint_x=None, width='80dp', font_size='14sp', background_color=BTN_DEFAULT)
        self.menu_right_btn.bind(on_press=self.toggle_right_menu)

        self.top_bar.add_widget(self.menu_left_btn)
        self.top_bar.add_widget(title)
        self.top_bar.add_widget(self.menu_right_btn)

        self.editor = CodeEditor(
            text='print("Hello, MobileIDE!")\n',
            font_size='16sp',
            background_color=(0.15, 0.15, 0.15, 1),
            foreground_color=TEXT_WHITE,
            cursor_color=TEXT_WHITE
        )

        self.output = TextInput(
            readonly=True,
            font_size='14sp',
            background_color=(0.1, 0.1, 0.1, 1),
            foreground_color=(0.8, 1, 0.8, 1),
            text="Готов к работе...",
            do_wrap=True
        )

        self.shortcut_bar = BoxLayout(size_hint_y=None, height='40dp', spacing=2)
        with self.shortcut_bar.canvas.before:
            Color(*THEME_COLOR)
            self.shortcut_bg = Rectangle(size=self.shortcut_bar.size, pos=self.shortcut_bar.pos)
        self.shortcut_bar.bind(size=self._update_shortcut_bg, pos=self._update_shortcut_bg)
        
        shortcuts = ["Tab", ":", "=", "(", ")", "[", "]", "{", "}", '"', "'", "+", "-"]
        for sym in shortcuts:
            btn = Button(text=sym, font_size='12sp', background_color=BTN_DEFAULT, color=TEXT_WHITE)
            btn.bind(on_press=lambda x, s=sym: self.insert_shortcut(s))
            self.shortcut_bar.add_widget(btn)

        self.main_content.add_widget(self.top_bar)
        self.main_content.add_widget(self.editor)
        self.main_content.add_widget(self.shortcut_bar)
        self.main_content.add_widget(self.output)

        # === ЛЕВОЕ МЕНЮ ===
        self.side_menu_left = BoxLayout(orientation='vertical', size_hint=(None, 1), width='220dp', pos_hint={'x': -1}, padding=10, spacing=10)
        with self.side_menu_left.canvas.before:
            Color(*MENU_BG_COLOR)
            self.menu_left_bg = Rectangle(size=self.side_menu_left.size, pos=self.side_menu_left.pos)
        self.side_menu_left.bind(size=self._update_left_bg, pos=self._update_left_bg)

        btn_save = Button(text="Сохранить", size_hint_y=None, height='45dp', background_color=BTN_DEFAULT, color=TEXT_WHITE)
        btn_save.bind(on_press=self.save_code)
        
        btn_export = Button(text="Экспорт в Загрузки", size_hint_y=None, height='45dp', background_color=BTN_DEFAULT, color=TEXT_WHITE)
        btn_export.bind(on_press=self.export_code)
        
        btn_font = Button(text="Размер шрифта", size_hint_y=None, height='45dp', background_color=BTN_DEFAULT, color=TEXT_WHITE)
        btn_font.bind(on_press=self.toggle_font_size)
        
        btn_search = Button(text="Поиск и Замена", size_hint_y=None, height='45dp', background_color=BTN_DEFAULT, color=TEXT_WHITE)
        btn_search.bind(on_press=self.show_search_popup)

        self.btn_toggle_output = Button(text="Скрыть вывод", size_hint_y=None, height='45dp', background_color=BTN_DEFAULT, color=TEXT_WHITE)
        self.btn_toggle_output.bind(on_press=self.toggle_output_panel)

        self.btn_run = Button(text="Запуск", size_hint_y=None, height='50dp', background_color=BTN_RUN, color=TEXT_BLACK, bold=True)
        self.btn_run.bind(on_press=self.run_code)

        self.side_menu_left.add_widget(Label(text="Действия", size_hint_y=None, height='40dp', bold=True, color=TEXT_BLACK))
        self.side_menu_left.add_widget(btn_save)
        self.side_menu_left.add_widget(btn_export)
        self.side_menu_left.add_widget(btn_font)
        self.side_menu_left.add_widget(btn_search)
        self.side_menu_left.add_widget(self.btn_toggle_output)
        self.side_menu_left.add_widget(self.btn_run)
        self.side_menu_left.add_widget(Label())

        # === ПРАВОЕ МЕНЮ ===
        self.side_menu_right = BoxLayout(orientation='vertical', size_hint=(None, 1), width='260dp', pos_hint={'x': 1}, padding=10, spacing=10)
        with self.side_menu_right.canvas.before:
            Color(*MENU_BG_COLOR)
            self.menu_right_bg = Rectangle(size=self.side_menu_right.size, pos=self.side_menu_right.pos)
        self.side_menu_right.bind(size=self._update_right_bg, pos=self._update_right_bg)

        header_layout = BoxLayout(size_hint_y=None, height='40dp')
        header_layout.add_widget(Label(text="Проекты", bold=True, color=TEXT_BLACK))
        
        import_btn = Button(text="Импорт", size_hint_x=None, width='70dp', background_color=BTN_DEFAULT, color=TEXT_WHITE)
        import_btn.bind(on_press=self.show_import_file_popup)
        new_file_btn = Button(text="+ Файл", size_hint_x=None, width='70dp', background_color=BTN_DEFAULT, color=TEXT_WHITE)
        new_file_btn.bind(on_press=self.show_new_file_popup)
        
        header_layout.add_widget(import_btn)
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
        self.shortcut_bg.pos = instance.pos
        self.shortcut_bg.size = instance.size

    def toggle_font_size(self, instance):
        if self.is_large_font:
            self.editor.font_size = '16sp'
            self.output.font_size = '14sp'
        else:
            self.editor.font_size = '20sp'
            self.output.font_size = '16sp'
        self.is_large_font = not self.is_large_font
        if self.menu_left_open: self.toggle_left_menu()

    def insert_shortcut(self, text):
        if not self.editor.focus: self.editor.focus = True
        if text == "Tab": self.editor.insert_text("    ")
        else: self.editor.insert_text(text)

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

    def refresh_files(self):
        self.files_layout.clear_widgets()
        files = [f for f in os.listdir(self.projects_dir) if f.endswith('.py')]
        if not files:
            with open(os.path.join(self.projects_dir, "main_script.py"), "w") as f:
                f.write('print("Hello, MobileIDE!")\n')
            files = ["main_script.py"]

        for filename in files:
            row = BoxLayout(size_hint_y=None, height='45dp', spacing=2)
            bg_color = (0.8, 0.6, 0.9, 1) if filename == self.current_file else BTN_DEFAULT
            txt_color = TEXT_BLACK if filename == self.current_file else TEXT_WHITE
            
            btn = Button(text=filename, background_color=bg_color, color=txt_color, halign='left')
            btn.bind(on_press=lambda x, fn=filename: self.load_file(fn))
            
            del_btn = Button(text="✕", size_hint_x=None, width='40dp', background_color=BTN_DELETE, color=TEXT_WHITE)
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
                if self.current_file == filename: self.load_file("main_script.py")
                else: self.refresh_files()
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

    def export_code(self, instance):
        if self.menu_left_open: self.toggle_left_menu()
        download_dir = "/storage/emulated/0/Download"
        if not os.path.exists(download_dir):
            self.output.text = "❌ Папка Download не найдена."
            return

        dest_path = os.path.join(download_dir, self.current_file)
        try:
            with open(dest_path, "w", encoding="utf-8") as f:
                f.write(self.editor.text)
            self.output.text = f"✅ Экспортировано в:\n{dest_path}"
        except Exception as e:
            self.output.text = f"❌ Ошибка экспорта (нет прав?): {e}"

    # === ИМПОРТ С ОБРАБОТКОЙ ОШИБОК ===
    def show_import_file_popup(self, instance):
        if self.menu_right_open: self.toggle_right_menu()
        try:
            filechooser.open_file(on_selection=self.handle_import_result)
        except Exception as e:
            self.output.text = f"❌ Ошибка вызова проводника: {e}"

    def handle_import_result(self, selection):
        if selection:
            source_path = selection[0]
            filename = os.path.basename(source_path)
            dest_path = os.path.join(self.projects_dir, filename)
            
            # Проверка на content:// URI (частая проблема Android 11+)
            if source_path.startswith("content://"):
                Clock.schedule_once(lambda dt: setattr(self.output, 'text', "❌ Ошибка: Android скрывает путь к файлу.\nЭкспортируй файл из другого приложения в папку 'Download' и попробуй снова."))
                return

            try:
                shutil.copy2(source_path, dest_path)
                Clock.schedule_once(lambda dt: self.load_file(filename))
                Clock.schedule_once(lambda dt: setattr(self.output, 'text', f"✅ Импортирован: {filename}"))
            except Exception as e:
                Clock.schedule_once(lambda dt: setattr(self.output, 'text', f"❌ Ошибка копирования: {e}"))
        else:
            Clock.schedule_once(lambda dt: setattr(self.output, 'text', "❌ Файл не выбран."))

    def show_search_popup(self, instance):
        if self.menu_left_open: self.toggle_left_menu()
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        find_input = TextInput(hint_text="Что искать...", multiline=False, size_hint_y=None, height='40dp')
        replace_input = TextInput(hint_text="На что заменить...", multiline=False, size_hint_y=None, height='40dp')
        btn_layout = BoxLayout(size_hint_y=None, height='40dp', spacing=10)
        btn_cancel = Button(text="Отмена", background_color=BTN_DELETE, color=TEXT_WHITE)
        btn_replace = Button(text="Заменить всё", background_color=BTN_RUN, color=TEXT_BLACK)
        btn_layout.add_widget(btn_cancel)
        btn_layout.add_widget(btn_replace)
        content.add_widget(Label(text="Поиск и замена", size_hint_y=None, height='30dp', color=TEXT_BLACK))
        content.add_widget(find_input)
        content.add_widget(replace_input)
        content.add_widget(btn_layout)
        popup = Popup(title="Поиск и Замена", content=content, size_hint=(0.9, 0.5))

        def do_replace(instance):
            find_text = find_input.text
            replace_text = replace_input.text
            if find_text:
                count = self.editor.text.count(find_text)
                self.editor.text = self.editor.text.replace(find_text, replace_text)
                self.output.text = f"Заменено вхождений: {count}"
                popup.dismiss()

        btn_cancel.bind(on_press=popup.dismiss)
        btn_replace.bind(on_press=do_replace)
        popup.open()

    # === СКРЫТИЕ ВЫВОДА С ИЗМЕНЕНИЕМ ТЕКСТА ===
    def toggle_output_panel(self, instance):
        if not self.output_hidden:
            self.output.height = 0
            self.output.size_hint_y = None
            self.output.opacity = 0
            self.btn_toggle_output.text = "Показать вывод"
            self.output_hidden = True
        else:
            self.output.size_hint_y = 1
            self.output.height = Window.height * 0.3
            self.output.opacity = 1
            self.btn_toggle_output.text = "Скрыть вывод"
            self.output_hidden = False
        if self.menu_left_open: self.toggle_left_menu()

    def show_new_file_popup(self, instance):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        text_input = TextInput(text="script", multiline=False, size_hint_y=None, height='40dp')
        btn_layout = BoxLayout(size_hint_y=None, height='40dp', spacing=10)
        btn_cancel = Button(text="Отмена", background_color=BTN_DELETE, color=TEXT_WHITE)
        btn_create = Button(text="Создать", background_color=BTN_RUN, color=TEXT_BLACK)
        btn_layout.add_widget(btn_cancel)
        btn_layout.add_widget(btn_create)
        content.add_widget(Label(text="Имя файла:", size_hint_y=None, height='30dp', color=TEXT_BLACK))
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

    def run_code(self, instance):
        code = self.editor.text
        self.output.text = "Выполняется..."
        self.btn_run.text = "ЗАПУЩЕНО"
        self.btn_run.background_color = (0.6, 0.2, 0.2, 1)

        if self.menu_left_open: self.toggle_left_menu()

        thread = threading.Thread(target=self._execute_code_in_thread, args=(code,))
        thread.daemon = True
        thread.start()

    def _execute_code_in_thread(self, code):
        old_stdout = sys.stdout
        sys.stdout = captured_output = io.StringIO()
        
        if self.projects_dir not in sys.path:
            sys.path.insert(0, self.projects_dir)

        try:
            exec(code, {"__name__": "__main__"})
            result = captured_output.getvalue()
            if not result: result = "[Код выполнен успешно]"
        except Exception:
            result = f"ОШИБКА:\n{traceback.format_exc()}"
        finally:
            sys.stdout = old_stdout
            Clock.schedule_once(lambda dt: self._finish_execution(result))

    def _finish_execution(self, result):
        self.output.text = result
        # Прокрутка в самый низ, чтобы увидеть конец вывода, 
        # но пользователь может скроллить вверх вручную.
        self.output.scroll_y = 0 
        self.btn_run.text = "Запуск"
        self.btn_run.background_color = BTN_RUN

class MobileIDEApp(App):
    def build(self):
        self.title = "MobileIDE v0.6"
        try:
            projects_dir = os.path.join(self.user_data_dir, "projects")
            if not os.path.exists(projects_dir):
                os.makedirs(projects_dir)
            return MainLayout(projects_dir=projects_dir)
        except Exception as e:
            return Label(text=f"Ошибка запуска:\n{e}", color=TEXT_BLACK)

if __name__ == '__main__':
    MobileIDEApp().run()