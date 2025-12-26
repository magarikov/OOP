

# Интерфейс
class Interface:
    def render_line(self, y, model, row, cursor_row, cursor_col, max_x):
        raise NotImplementedError


#   БАЗОВЫЙ РЕНДЕРЕР - выводит текст без форматирования
class Base(Interface):
    def __init__(self, ui):
        self.ui = ui

    def render_line(self, y, model, row, cursor_row, cursor_col, max_x):
        # Простой вывод строки без украшений.
        text = model.get_line(row).c_str()
        if isinstance(text, bytes):
            text = text.decode("latin1")

        text = text[:max_x - 1]   # обрезаем по ширине терминала
        self.ui.addstr(y, 0, text, self.ui.color_map.get('normal'))
        return 0  # Базовый рендерер выводит с 0 отступом

#   ДЕКОРАТОР: ПОДСВЕТКА СИНТАКСИСА
class SyntaxDecorator(Interface):
    def __init__(self, wrapped: Interface):
        self.wrapped = wrapped
        self.ui = wrapped.ui

    def render_line(self, y, model, row, cursor_row, cursor_col, max_x):
        indent = self.wrapped.render_line(y, model, row, cursor_row, cursor_col, max_x)

        if not model.highlight_enabled:
            return indent  # если подсветка выключена — ничего не делаем

        spans = model.get_syntax_str(row, lang='c')

        x = indent # начинаем рисовать подсветку с того же отступа, с которого начал Base
        for text, ttype in spans:
            if x >= max_x - 1:
                break
            out = text[:max_x - 1 - x]
            self.ui.addstr(y, x, out, self.ui.color_map.get(ttype, self.ui.color_map["normal"]))
            x += len(out)

        return indent


# КОНЕЧНЫЙ ВИД - использует цепочку декораторов
class TextView:
    def __init__(self, ui, show_numbers=True):
        self.ui = ui
        self.show_numbers = show_numbers

        # строим очередь из декораторов
        renderer: Interface = Base(ui)

        # подсветка - всегда вызывается, но вкл/выкл через model.highlight_enabled
        renderer = SyntaxDecorator(renderer)

        self.renderer = renderer

    def screen(self, model, cursor_row, cursor_col, mode, cmd_buffer=""):
        self.ui.clear()
        max_y, max_x = self.ui.getmaxyx()
        height = max_y - 1

        start_row = max(0, cursor_row - height//2)
        if start_row + height > model.line_count():
            start_row = max(0, model.line_count() - height)

        for screen_row in range(height):
            
            model_row = start_row + screen_row
            y = screen_row
            x = 0
            
            self.renderer.render_line(y, model, model_row, cursor_row, cursor_col, max_x)
            # встроенные номера строк (как было раньше)
            if self.show_numbers:
                num = f"{model_row+1:4d} "
                self.ui.addstr(screen_row, 0, num)
                x += len(num)
            
        # строка состояния
        filename = model.filename or "[NoName]"
        status = f"{mode} | {filename} | {cursor_row+1}/{model.line_count()}"
        if cmd_buffer:
            status += " | :" + cmd_buffer
        self.ui.addstr(max_y - 1, 0, status[:max_x-1])

        # позиция курсора (компенсация номеров строк)
        screen_y = cursor_row - start_row
        screen_x = cursor_col

        self.ui.move(screen_y, max(0, min(screen_x, max_x-1)))
        self.ui.refresh()


'''
class TextView:
    def __init__(self, ui_adapter):
        self.ui = ui_adapter
        # флаг отображения номеров строк (команда set num)
        self.show_numbers = True


    def screen(self, model, cursor_row, cursor_col, mode, cmd_buffer=""):
        self.ui.clear()
        max_y, max_x = self.ui.getmaxyx()
        height = max_y - 1

        start_row = max(0, cursor_row - height//2)
        if start_row + height > model.line_count():
            start_row = max(0, model.line_count() - height)

        for screen_row in range(height):
            model_row = start_row + screen_row
            if model_row >= model.line_count():
                break

            # если подсветка включена - получаем фрагменты от модели
            if getattr(model, "highlight_enabled", False):
                spans = model.get_syntax_str(model_row, lang='c')
                # если нужно — добавляем номер строки вначале как отдельный фрагмент
                x = 0
                if self.show_numbers:
                    num = f"{model_row+1:4d} "
                    self.ui.addstr(screen_row, x, num, self.ui.color_map.get('normal'))
                    x += len(num)
                # отрисовываем каждый фрагмент с цветом
                for text, ttype in spans:
                    # обрезаем до правой границы экрана
                    if x >= max_x - 1:
                        break
                    maxlen = max_x - 1 - x
                    out = text[:maxlen]
                    attr = self.ui.color_map.get(ttype, self.ui.color_map.get('normal'))
                    self.ui.addstr(screen_row, x, out, attr)
                    x += len(out)
            else:
                # обычный вывод без подсветки
                line = model.get_line(model_row)
                content = line.c_str()
                s = content.decode("latin1") if isinstance(content, bytes) else str(content)
                if self.show_numbers:
                    display = f"{model_row+1:4d} " + s
                else:
                    display = s
                self.ui.addstr(screen_row, 0, display[:max_x-1])

        # строка состояния
        filename = model.filename or "[NoName]"
        status = f"{mode} | {filename} | {cursor_row+1}/{model.line_count()}"
        if cmd_buffer:
            status += " | :" + cmd_buffer
        self.ui.addstr(max_y - 1, 0, status[:max_x-1])

        # позиция курсора
        screen_y = cursor_row - start_row
        screen_x = cursor_col + (5 if self.show_numbers else 0)
        self.ui.move(screen_y, max(0, min(screen_x, max_x-1)))
        self.ui.refresh()

    def screen_help(self):
        self.ui.clear()
        max_y, max_x = self.ui.getmaxyx()

        help_text = [
            "Основные команды:",
            "  i — начать ввод",
            "  h,j,k,l или стрелки — перемещение",
            "  dd — удалить строку",
            "  yy — копировать строку",
            "  p — вставить строку",
            "  :w — сохранить",
            "  :q — выйти",
            "  :set num — номера строк",
            "  /текст — поиск вперёд",
            "  ?текст — поиск назад",
            "  ESC — выход из режима помощи",
        ]

        for i, line in enumerate(help_text):
            if i < max_y - 1:
                self.ui.addstr(i, 0, line[:max_x-1])

        self.ui.addstr(max_y - 1, 0, "Нажмите ESC, чтобы выйти.")
        self.ui.refresh()


'''