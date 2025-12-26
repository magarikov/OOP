
import curses

# Отделяет детали curses от логики View/Controller.
class CursesAdapter:

    def init(self):
        self.screen = curses.initscr()
        curses.noecho()
        curses.cbreak()
        self.screen.keypad(True)
        try:
            curses.curs_set(1)
        except curses.error:
            pass

        # Инициализация цветов, если поддерживаются
        if curses.has_colors():
            curses.start_color()
            # пары: индекс, fg, bg
            # здесь пример цветов; можно менять
            curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLACK)   # keyword
            curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)     # type
            curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)    # string
            curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK)     # comment
            curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)  # number
            curses.init_pair(6, curses.COLOR_RED, curses.COLOR_BLACK)      # func
            # заполняем карту по именам
            
            self.color_map = {
                'keyword': curses.color_pair(5),
                'type': curses.color_pair(4) | curses.A_BOLD,
                'string': curses.color_pair(1),
                'comment': curses.color_pair(3) | curses.A_BOLD,
                'number': curses.color_pair(2) | curses.A_BOLD,
                'func': curses.color_pair(1) | curses.A_BOLD,
                'normal': curses.A_NORMAL
            }
        else:
            # если цветов нет, все равно создаём карту с нормальными атрибутами
            self.color_map = {k: curses.A_NORMAL for k in ['keyword','type','string','comment','number','func','normal']}


    def shutdown(self):
        # завершение работы curses
        if not self.screen:
            return
        curses.nocbreak()
        self.screen.keypad(False)
        curses.echo()
        try:
            curses.curs_set(1)
        except curses.error:
            pass
        curses.endwin()
        self.screen = None

    def clear(self):
        self.screen.clear()

    def refresh(self):
        self.screen.refresh()

    def getch(self):
        return self.screen.getch()

    # теперь поддерживаем опциональный attr
    def addstr(self, y, x, text, attr=None):
        try:
            if attr is None:
                self.screen.addstr(y, x, text)
            else:
                self.screen.addstr(y, x, text, attr)
        except curses.error:
            pass

    def move(self, y, x):
        try:
            self.screen.move(y, x)
        except curses.error:
            pass

    def getmaxyx(self):
        return self.screen.getmaxyx()
