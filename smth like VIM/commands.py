
class ICommand:
    def execute(self) -> bool:
        raise NotImplementedError()


class OpenCommand(ICommand):
    def __init__(self, editor, filename):
        self.editor = editor
        self.filename = filename

    def execute(self):
        try:
            self.editor.model.load_file(self.filename)
            self.editor.cursor_row = 0
            self.editor.cursor_col = 0
        except Exception as e:
            print(f"Ошибка открытия файла: {e}")
        return True


class WriteCommand(ICommand):
    def __init__(self, editor):
        self.editor = editor

    def execute(self):
        if self.editor.model.filename:
            self.editor.model.save_file()
        else:
            print("Нет имени файла. Используйте :w имя_файла")
        return True


class WriteAsCommand(ICommand):
    def __init__(self, editor, filename):
        self.editor = editor
        self.filename = filename

    def execute(self):
        self.editor.model.save_file(self.filename)
        return True


class QuitCommand(ICommand):
    def __init__(self, editor):
        self.editor = editor

    def execute(self):
        if self.editor.model.modified:
            print("Есть несохранённые изменения. Используйте :q! для выхода без сохранения")
            return True
        return False


class QuitForceCommand(ICommand):
    def execute(self):
        return False


class WriteQuitCommand(ICommand):
    def __init__(self, editor):
        self.editor = editor

    def execute(self):
        if self.editor.model.filename:
            self.editor.model.save_file()
        return False


class GotoLineCommand(ICommand):
    def __init__(self, editor, line):
        self.editor = editor
        self.line = line

    def execute(self):
        if 1 <= self.line <= self.editor.model.line_count():
            self.editor.cursor_row = self.line - 1
            self.editor.cursor_col = 0
        return True


class ToggleNumbersCommand(ICommand):
    def __init__(self, editor):
        self.editor = editor

    def execute(self):
        self.editor.show_numbers = not self.editor.show_numbers
        return True


class HelpCommand(ICommand):
    def __init__(self, editor):
        self.editor = editor

    def execute(self):
        self.editor.mode = "HELP"
        while True:
            self.editor.view.screen_help()
            key = self.editor.ui.getch()
            if key == 27:  # ESC
                break
        self.editor.mode = "NORMAL"
        return True


class ToggleSyntaxCommand(ICommand):
    def __init__(self, editor):
        self.editor = editor

    def execute(self):
        self.editor.model.toggle_syntax_highlight()
        return True


class UnknownCommand(ICommand):
    def __init__(self, cmd):
        self.cmd = cmd

    def execute(self):
        print(f"Неизвестная команда: {self.cmd}")
        return True
