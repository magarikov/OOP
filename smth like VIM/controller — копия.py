
import curses
from MyString import MyString

ESC = 27
ENTER = 10
BACKSPACE = 8
PG_UP = 338
PG_DOWN = 339

def log(message):
    with open('log.txt', 'a', encoding='utf-8') as f:
        f.write(message + '\n')



class Command:
    def __init__(self, editor, cmd):
        self.editor = editor  # кто редактирует (т.е. контроллер получается)
        self.cmd = cmd.strip() # .strip() убирает пробелы в начале и конце

    def execute(self) -> bool:
        if not self.cmd:
            return True

        # o filename - открыть файл
        if self.cmd.startswith("o "):
            filename = self.cmd[2:].strip()
            try:
                self.editor.model.load_file(filename)
                self.editor.cursor_row = 0
                self.editor.cursor_col = 0
            except Exception as e:
                print(f"Ошибка открытия файла: {e}")
            return True

        # w - сохранить в текущий файл
        if self.cmd == "w":
            if self.editor.model.filename:
                self.editor.model.save_file()
            else:
                print("Нет имени файла. Используйте :w имя_файла")
            return True

        # w filename - сохранить как
        if self.cmd.startswith("w "):
            filename = self.cmd[2:].strip()
            self.editor.model.save_file(filename)
            return True

        # q - выйти (если нет изменений)
        if self.cmd == "q":
            if self.editor.model.modified:
                print("Есть несохранённые изменения. Используйте :q! для выхода без сохранения")
                return True
            return False

        # q! - выйти насильно
        if self.cmd == "q!":
            return False

        # wq!, x - сохранить и выйти
        if self.cmd in ("wq!", "x"):
            if self.editor.model.filename or " " in self.cmd:
                # если есть имя файла - сохраняем
                if self.editor.model.filename:
                    self.editor.model.save_file()
            return False

        # номер строки - перейти на строку
        if self.cmd.isdigit():
            line_num = int(self.cmd)
            if 1 <= line_num <= self.editor.model.line_count():
                self.editor.cursor_row = line_num - 1
                self.editor.cursor_col = 0
            return True

        # set num - включить/выключить нумерацию строк
        if self.cmd == "set num":
            self.editor.show_numbers = not self.editor.show_numbers
            return True

        # h - помощь
        if self.cmd == "h":
            self.editor.mode = "HELP"
            while True:
                self.editor.view.screen_help()
                key = self.editor.ui.getch()
                if key == 27:  # ESC
                    break
            self.editor.mode = "NORMAL"
            return True

        # sy - включить/выключить подсветку синтаксиса
        if self.cmd == "sy":
            self.editor.model.toggle_syntax_highlight()
            return True

        # Неизвестная команда
        print(f"Неизвестная команда: {self.cmd}")
        return True



class Controller:
    def __init__(self, model, view, ui):
        self.model = model
        self.view = view       # УЖЕ собранная цепочка
        self.ui = ui

        # курсор 
        self.cursor_row = 0
        self.cursor_col = 5

        self.last_search = None          # строка поиска
        self.last_search_direction = None  # "forward" или "backward"

        # режим: "NORMAL", "INSERT", "COMMAND", "SEARCH_FWD", "SEARCH_BWD, HELP"
        self.mode = "NORMAL"
        self.cmd_buffer = ""  # буфер для ":" команд
        self.search_buffer = ""
        self.clipboard_line = None  # для yy / p
        self.last_search = None
        self.show_numbers = True

    def run(self):
        while True:
            # синхронизируем настройку номеров строк в view
            self.view.show_numbers = self.show_numbers
            self.view.screen(self.model, self.cursor_row, self.cursor_col, self.mode, self.cmd_buffer if self.mode=="COMMAND" else "")
            key = self.ui.getch()
            
            # обработка в зависимости от режима
            if self.mode == "NORMAL":

                if key == ord('i'):
                    self.mode = "INSERT"
                elif key == ord('I'):
                    self.cursor_col = 5
                    self.mode = "INSERT"
                elif key == ord('A'):
                    # перейти в конец строки и вставить
                    line = self.model.get_line(self.cursor_row)
                    content = line.c_str()
                    if isinstance(content, bytes):
                        s = content.decode("latin1")
                    else:
                        s = str(content)
                    self.cursor_col = len(s)
                    self.mode = "INSERT"
                elif key == ord('o'):
                    # вставить пустую строку ниже и перейти в insert
                    self.model.insert_empty_line_after(self.cursor_row)
                    self.cursor_row += 1
                    self.cursor_col = 5
                    self.mode = "INSERT"
                elif key == ord(':'):
                    self.mode = "COMMAND"
                    self.cmd_buffer = ""
                elif key == ord('/'):
                    self.mode = "SEARCH_FWD"
                    self.search_buffer = ""
                elif key == ord('?'):
                    self.mode = "SEARCH_BWD"
                    self.search_buffer = ""
                elif key == ord('h') or key == curses.KEY_LEFT:
                    self.move_left()
                elif key == ord('l') or key == curses.KEY_RIGHT:
                    self.move_right()
                elif key == ord('k') or key == curses.KEY_UP:
                    self.move_up()
                elif key == ord('j') or key == curses.KEY_DOWN:
                    self.move_down()
                elif key == ord('0') or key == ord('^'):
                    self.cursor_col = 5
                elif key == ord('$'):
                    line = self.model.get_line(self.cursor_row)
                    content = line.c_str()
                    if isinstance(content, bytes):
                        s = content.decode("latin1")
                    else:
                        s = str(content)
                    self.cursor_col = len(s)
                elif key == ord('w'):
                    self.word_move_forward()
                elif key == ord('b'):
                    self.word_move_back()
                elif key == ord('g'):
                    # поддерживаем gg (двойное g)
                    key2 = self.ui.getch()
                    if key2 == ord('g'):
                        self.cursor_row = 0
                        self.cursor_col = 5
                elif key == ord('G'):
                    self.cursor_row = self.model.line_count() - 1
                    self.cursor_col = 5
                elif key == ord('x'):
                    # удалить символ после курсора
                    self.model.erase(self.cursor_row, self.cursor_col, 1)
                elif key == ord('d'):
                    # ожидаем второй символ (dd = удалить строку)
                    key2 = self.ui.getch()
                    if key2 == ord('d'):
                        self.model.delete_line(self.cursor_row)
                        # скорректировать курсор
                        if self.cursor_row >= self.model.line_count():
                            self.cursor_row = self.model.line_count() - 1
                        self.cursor_col = min(self.cursor_col, self._line_length(self.cursor_row))
                    elif key2 == ord('i'):
                        key3 = self.ui.getch()
                        if key3 == ord('w'):
                            # удалить слово под курсором (diw)
                            line = self.model.get_line(self.cursor_row)
                            content = line.c_str()
                            start = self.cursor_col
                            if start == len(content):
                                continue
                            delete_len, start = self.model.delete_word(content, start)

                            if delete_len > 0:
                                self.model.erase(self.cursor_row, start, delete_len)

                            self.cursor_col = start

                            


                elif key == ord('y'):
                    key2 = self.ui.getch()
                    if key2 == ord('y'):
                        # копировать текущую строку
                        self.clipboard_line = self.model.copy_line(self.cursor_row) 
                     # yw - копировать слово под курсором
                    elif key2 == ord('w'):
                        line = self.model.get_line(self.cursor_row).c_str()
                        if isinstance(line, bytes):
                            s = line.decode("latin1")
                        else:
                            s = str(line)

                        start = self.cursor_col
                        while start > 0 and s[start - 1].isalnum():
                            start -= 1

                        end = start
                        while end < len(s) and s[end].isalnum():
                            end += 1

                        self.clipboard_line = s[start:end]

                elif key == ord('p'):
                    if self.clipboard_line is not None:
                        # Получить текущую строку
                        line = self.model.get_line(self.cursor_row)
                        col = self.cursor_col

                        # Вставить содержимое буфера в текущую строку
                        line.insert(col, self.clipboard_line)

                        # Переместить курсор после вставленного текста
                        self.cursor_col += len(self.clipboard_line)

                elif key == ord('S'):
                    # удалить содержимое текущей строки и перейти в insert (S)
                    self.model.replace_line(self.cursor_row, "")
                    self.cursor_col = 5
                    self.mode = "INSERT"
                elif key == ord('r'):
                    # заменяем один символ под курсором
                    # читаем следующий символ
                    k = self.ui.getch()
                    ch = chr(k)
                    # заменить: удалить и вставить
                    self.model.erase(self.cursor_row, self.cursor_col, 1)
                    self.model.insert_char(self.cursor_row, self.cursor_col, ch)
                elif key == ord('u'):
                    # undo не реализован в базовой версии
                    pass
                elif key == ord('s'):
                    # 's' - удалить один символ и войти в insert (как vim)
                    self.model.erase(self.cursor_row, self.cursor_col, 1)
                    self.mode = "INSERT"
                elif key == ord('^') or key == ord('0'):
                    self.cursor_col = 5
                elif key >= ord("1") and key <= ord("9"): # 10N поиск
                    str_num = key - ord("0") # 48 - код нуля
                    flag = 1
                    while 1:
                        key = self.ui.getch()
                        if key >= ord("0") and key <= ord("9"):
                                str_num = str_num * 10 + key - ord("0")
                        elif key == ord("G"):
                            break
                        else:
                            flag = 0 # если нажали что-то другое, скипаем
                            break

                    if (flag and str_num > 0 and str_num < self.model.line_count()):
                        str_num -= 1
                        self.cursor_row = str_num
                        self.cursor_col = 5

                elif key == PG_UP:
                    self.cursor_row += 29
                    if (self.cursor_row > self.model.line_count() - 1):
                        self.cursor_row = self.model.line_count() - 1
                elif key == PG_DOWN:
                    self.cursor_row -= 29
                    if (self.cursor_row < 0):
                        self.cursor_row = 0

                elif key == ord('n'):
                    # повторить поиск в том же направлении
                    if self.last_search:
                        if self.last_search_direction == "forward":
                            found = self.model.find_forward(self.cursor_row + 1, self.last_search)
                        else:
                            found = self.model.find_backward(self.cursor_row - 1, self.last_search)

                        if found != -1:
                            self.cursor_row = found
                            self.cursor_col = 5

                elif key == ord('N'):
                    # повторить поиск в обратном направлении
                    if self.last_search:
                        if self.last_search_direction == "forward":
                            # обратное направление
                            found = self.model.find_backward(self.cursor_row - 1, self.last_search)
                        else:
                            # обратное направление
                            found = self.model.find_forward(self.cursor_row + 1, self.last_search)

                        if found != -1:
                            self.cursor_row = found
                            self.cursor_col = 5

                # прочие клавиши игнорируем



            elif self.mode == "INSERT":
                if key == ESC:
                    self.mode = "NORMAL"
                elif key == ENTER:
                    # делаем split line на текущей позиции
                    new_row = self.model.split_line(self.cursor_row, self.cursor_col)
                    self.cursor_row = new_row
                    self.cursor_col = 5

                elif key == BACKSPACE:
                    # backspace: удалить символ слева от курсора
                    if self.cursor_col > 0:
                        self.model.erase(self.cursor_row, self.cursor_col-1, 1)
                        self.cursor_col -= 1
                    else:
                        # если в начале строки - объединить с предыдущей
                        if self.cursor_row > 5:
                            prev_len = self._line_length(self.cursor_row - 1)
                            self.model.join_with_next(self.cursor_row - 1)
                            self.cursor_row -= 1
                            self.cursor_col = prev_len

                elif (key >= 32) and (key <= 125):
                    
                    # обычная печатная клавиша
                    ch = chr(key)
                    self.model.insert_char(self.cursor_row, self.cursor_col, ch)
                    self.cursor_col += 1



            elif self.mode == "COMMAND":
                
                if key == ESC:
                    self.mode = "NORMAL"
                elif key == ENTER:
                    cont = self.process_colon_command(self.cmd_buffer)
                    self.cmd_buffer = ""
                    self.mode = "NORMAL"
                    # после выполнения команды сразу возвращаемся в норм 
                    if cont is False:
                        return  # выход из приложения
                    
                elif key == BACKSPACE:
                    self.cmd_buffer = self.cmd_buffer[:-1]
                    self.cursor_col -= 1

                elif (key >= 32) and (key <= 125):
                    self.cmd_buffer += chr(key)

                    
            elif self.mode in ("SEARCH_FWD", "SEARCH_BWD"):
                if key == ESC:
                    self.mode = "NORMAL"

                elif key == ENTER:
                    needle = self.search_buffer
                    if self.mode == "SEARCH_FWD":
                        found = self.model.find_forward(self.cursor_row, needle)
                        self.last_search_direction = "forward"
                    else:
                        found = self.model.find_backward(self.cursor_row, needle)
                        self.last_search_direction = "backward"

                    if found != -1:
                        self.cursor_row = found
                        self.cursor_col = 5
                        self.last_search = needle

                    self.mode = "NORMAL"
                    self.search_buffer = ""

                else:
                    self.search_buffer += chr(key)

            # elif HELP находится ниже
            
            else:
                try:
                    self.search_buffer += chr(key)
                except:
                    pass


    # ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ 
    def _line_length(self, row):
        ln = self.model.get_line(row).c_str()
        if isinstance(ln, bytes):
            s = ln.decode("latin1")
        else:
            s = str(ln)
        return len(s)

    def move_left(self):
        if self.cursor_col > 5:
            self.cursor_col -= 1

    def move_right(self):
        self.cursor_col = min(self._line_length(self.cursor_row), self.cursor_col + 1)

    def move_up(self):
        if self.cursor_row > 0:
            self.cursor_row -= 1
            self.cursor_col = min(self.cursor_col, self._line_length(self.cursor_row))

    def move_down(self):
        if self.cursor_row < self.model.line_count() - 1:
            self.cursor_row += 1
            self.cursor_col = min(self.cursor_col, self._line_length(self.cursor_row))

    def word_move_forward(self):
        # перейти к концу слова справа
        ln = self.model.get_line(self.cursor_row).c_str()
        if isinstance(ln, bytes):
            s = ln.decode("latin1")
        else:
            s = str(ln)
        target = self.model.find_word_end(s, self.cursor_col)
        # если target == len(s) означает переход на конец строки
        if target >= len(s):
            self.cursor_col = len(s)
        else:
            self.cursor_col = target + 1  # position at end of word

    def word_move_back(self):
        ln = self.model.get_line(self.cursor_row).c_str()
        if isinstance(ln, bytes):
            s = ln.decode("latin1")
        else:
            s = str(ln)
        target = self.model.find_word_start_left(s, self.cursor_col)
        self.cursor_col = target

    def process_colon_command(self, cmd):
        command = Command(self, cmd)    # создаём объект-команду
        return command.execute()


# Для распознавания клавиш Ctrl/стрелок используем этот helper чтобы не тащить curses сюда:
def curses_key(name):
    """
    Возвращает псевдокод для стрелок/backspace - в реальном приложении используйте curses.KEY_LEFT и т.д.
    Здесь ставим простую маппу, чтобы код контроллера читался.
    """
    # числовые коды стандартных значений (в большинстве терминалов)
    mapping = {
        
    }
    return mapping.get(name, -1)
