
#Model: хранит текст как список строк (каждая строка - MyString).
#Работает в 1-байтовой кодировке (latin1).
from MyString import MyString
import re
class TextModel:
    def __init__(self, filename=None):
        # Строки храним как список объектов MyString
        self.lines = [MyString("")]
        self.filename = filename
        self.modified = False

        self.highlight_enabled = False

    # gереключение подсветки синтаксиса
    def toggle_syntax_highlight(self):
        
        self.highlight_enabled = not self.highlight_enabled

    # возвращает список (text, token_type) для строки row 
    def get_syntax_str(self, row, lang='c'):

        # Берём строку из модели
        raw = self.get_line(row).c_str()
        if isinstance(raw, bytes):
            s = raw.decode("latin1")
        else:
            s = str(raw)

        # простая схема токенизации (приоритет важен):
        # 1 комментарии (//...)
        # 2 строки
        # 3 числа
        # 4 идентификаторы (включая имена функций)
        # 5 прочее - оставляем как normal

        spans = []
        idx = 0
        n = len(s)

        # предопределённые множества (можно расширять)
        keywords = {
            'if','else','for','while','switch','case','break','continue','return',
            'goto', 'do', 'sizeof', 'static', 'extern', 'register', 'volatile'
        }
        types = {
            'int','char','short','long','float','double','void','signed','unsigned','struct','union','const', 'enum'
        }

        # компилируем регулярки
        # комментарий //...
        comment_re = re.compile(r'//.*')
        # строковый литерал (обработка escaped не полная, но достаточна)
        string_re = re.compile(r'"([^"\\]|\\.)*"|\'([^\'\\]|\\.)*\'')
        number_re = re.compile(r'\b\d+(\.\d+)?([eE][+-]?\d+)?\b')
        ident_re = re.compile(r'\b[_A-Za-z][_A-Za-z0-9]*\b')

        # функция-помощник: добавить "normal" фрагмент (если текст не пуст)
        def push_normal(t):
            if t:
                spans.append((t, 'normal'))

        pos = 0
        while pos < n:
            # 1 комментарий
            m = comment_re.match(s, pos)
            if m:
                spans.append((m.group(0), 'comment'))
                break  # комментарий до конца строки
            # 2 строка
            m = string_re.match(s, pos)
            if m:
                spans.append((m.group(0), 'string'))
                pos = m.end()
                continue
            # 3 число
            m = number_re.match(s, pos)
            if m:
                spans.append((m.group(0), 'number'))
                pos = m.end()
                continue
            # 4 идентификатор / ключевое слово / тип / имя функции
            m = ident_re.match(s, pos)
            if m:
                tok = m.group(0)
                end = m.end()
                # выясним, это имя функции? — простая эвристика: следующий непробельный символ '('
                after = s[end:].lstrip()
                if tok in keywords:
                    spans.append((tok, 'keyword'))
                elif tok in types:
                    spans.append((tok, 'type'))
                elif after.startswith('('):
                    # имя функции (наивная эвристика)
                    spans.append((tok, 'func'))
                else:
                    spans.append((tok, 'normal'))
                pos = end
                continue
            # 5 прочие символы (операторы, пробелы и т.д.) — возьмём один символ
            spans.append((s[pos], 'normal'))
            pos += 1

        # объединяем соседние фрагменты одного типа для удобства (уменьшает кол-во addstr)
        merged = []
        for text, ttype in spans:
            if merged and merged[-1][1] == ttype:
                merged[-1] = (merged[-1][0] + text, ttype)
            else:
                merged.append((text, ttype))
        return merged


    # ----------------- ФАЙЛОВЫЕ ОПЕРАЦИИ -----------------
    def load_file(self, filename):

        # пробуем открыть
        try: 
            self.lines = []
            with open(filename, "r", encoding="latin1") as f:
                for ln in f:
                    # удаляем завершающий '\n'
                    s = ln.rstrip("\n")
                    self.lines.append(MyString("     ") + MyString(s))
            if not self.lines:
                self.lines = [MyString("")]
            self.filename = filename
            self.modified = False

        # Если не нашли - создаем
        except FileNotFoundError:
            self.lines = [MyString("")]
            if filename != '':
                open(filename, 'w', encoding='utf-8')
                    

    def save_file(self, filename=None):
        """Сохранить в файл (latin1)."""
        if filename is None:
            filename = self.filename

        with open(filename, "w", encoding="latin1", errors="ignore") as f:
            for ln in self.lines:
                # ln.c_str() возвращает bytes/char* — в pybind11 мы предполагаем строку байтовой кодировки.
                # Некоторые реализации MyString.c_str() могут вернуть bytes или str; безопасно приводим:
                content = ln.c_str()
                if isinstance(content, bytes):
                    s = content.decode("latin1")
                else:
                    s = str(content)
                f.write(s + "\n")
        self.filename = filename
        self.modified = False

    # ----------------- ДОСТУП И СТАТИСТИКА -----------------
    def line_count(self):
        return len(self.lines)

    def get_line(self, idx):
        return self.lines[idx]

    # ----------------- РЕДАКТИРОВАНИЕ -----------------
    def insert_char(self, row, col, ch):
        
        # Вставить символ ch (один символ Python str) в строку row на позицию col.
        # ch должен быть строкой длиной 1.
        
        if row < 0 or row >= len(self.lines):
            raise IndexError("Row out of range")
        line = self.lines[row]
        # MyString.insert поддерживает разные сигнатуры; пытаемся наиболее простую:
        # вставка 1 символа: insert(pos, 1, ch_char) — в вашей обертке есть сигнатура (int, int, char)
        try:
            line.insert(col, 1, ch)  # если ваша сигнатура ожидает char (C) - pybind не всегда поддерживает
        except Exception:
            # Альтернативный: взять c_str, сформировать новую строку и заменить
            content = line.c_str()
            if isinstance(content, bytes):
                s = content.decode("latin1")
            else:
                s = str(content)
            s = s[:col] + ch + s[col:]
            line.clear()
            line.append(s)
        self.modified = True

    def append_to_line(self, row, s):
        # Добавить строку s в конец строки row.
        line = self.lines[row]
        try:
            line.append(s)
        except Exception:
            content = line.c_str()
            if isinstance(content, bytes):
                cur = content.decode("latin1")
            else:
                cur = str(content)
            new = cur + s
            line.clear()
            line.append(new)
        self.modified = True

    def erase(self, row, col, length=1):
        # Удалить length символов, начиная с позиции col в строке row.
        line = self.lines[row]
        try:
            line.erase(col, length)
        except Exception:
            # fallback: ручное редактирование
            content = line.c_str()
            if isinstance(content, bytes):
                s = content.decode("latin1")
            else:
                s = str(content)
            s = s[:col] + s[col+length:]
            line.clear()
            line.append(s)
        self.modified = True

    def split_line(self, row, col):
        
        # Разделить строку row на две в позиции col:
        # верхняя часть остаётся в row, нижняя вставляется под row.
        # Возвращает индекс новой строки.
        
        line = self.lines[row]
        content = line.c_str()
        if isinstance(content, bytes):
            s = content.decode("latin1")
        else:
            s = str(content)
        left = s[:col]
        right = s[col:]
        line.clear()
        line.append(left)
        self.lines.insert(row + 1, MyString(right))
        self.modified = True
        return row + 1

    def join_with_next(self, row):
        # Объединить строку row с следующей строкой (удалив перевод строки).
        if row + 1 >= len(self.lines):
            return
        cur = self.lines[row].c_str()
        nxt = self.lines[row+1].c_str()
        if isinstance(cur, bytes):
            cur_s = cur.decode("latin1")
        else:
            cur_s = str(cur)
        if isinstance(nxt, bytes):
            nxt_s = nxt.decode("latin1")
        else:
            nxt_s = str(nxt)
        new = cur_s + nxt_s
        self.lines[row].clear()
        self.lines[row].append(new)
        del self.lines[row+1]
        self.modified = True

    # Утилитарные методы
    def replace_line(self, row, s):
        self.lines[row].clear()
        self.lines[row].append(s)
        self.modified = True

    def insert_empty_line_after(self, row):
        self.lines.insert(row+1, MyString(""))
        self.modified = True

    def delete_line(self, row):
        del self.lines[row]
        if not self.lines:
            self.lines = [MyString("")]
        self.modified = True

    def delete_word(self, content, start):
        if isinstance(content, bytes):
            s = content.decode("latin1")
        else:
            s = str(content)
        
        while content[start] != ' ' and start > 0:
            start -= 1
        if start != 0:
            start += 1

        end = start
        while end < len(content) and content[end] != ' ':
            end += 1
        
        if end < len(s) and s[end] == ' ':
            end += 1
        delete_len = end - start
        return delete_len, start

        

    def copy_line(self, row):
        # возврат копии строки как Python str (latin1)
        c = self.lines[row].c_str()
        if isinstance(c, bytes):
            return c.decode("latin1")
        return str(c)

    # Поиск: простая реализация (поиск строки в каждой строке)
    def find_forward(self, start_row, needle):
        # Поиск needle от start_row до конца; возвращает индекс строки или -1.
        for i in range(start_row, len(self.lines)):
            ln = self.lines[i].c_str()
            if isinstance(ln, bytes):
                s = ln.decode("latin1")
            else:
                s = str(ln)
            if needle in s:
                return i
        return -1

    def find_backward(self, start_row, needle):
        # Поиск needle от start_row до начала; возвращает индекс строки или -1.
        for i in range(start_row, -1, -1):
            ln = self.lines[i].c_str()
            if isinstance(ln, bytes):
                s = ln.decode("latin1")
            else:
                s = str(ln)
            if needle in s:
                return i
        return -1


    def is_word_char(ch):
        return ch.isalnum() or ch == '_'

    def find_word_end(s, pos):
        # найти конец слова справа от pos (если pos на границе слова - переход к следующему)
        n = len(s)
        # если в пределах и внутри слова - прыгнуть к концу текущего слова
        if pos < n and is_word_char(s[pos]):
            i = pos
            while i < n and is_word_char(s[i]):
                i += 1
            return i - 1
        # иначе перейти к началу следующего слова, затем к его концу
        i = pos
        while i < n and not is_word_char(s[i]):
            i += 1
        if i == n:
            return n
        while i < n and is_word_char(s[i]):
            i += 1
        return i - 1

    def find_word_start_left(s, pos):
        # найти начало слова слева от pos
        if pos > 0 and is_word_char(s[pos-1]):
            i = pos-1
            while i >= 0 and is_word_char(s[i]):
                i -= 1
            return i + 1
        i = pos-1
        while i >= 0 and not is_word_char(s[i]):
            i -= 1
        if i < 0:
            return 0
        while i >= 0 and is_word_char(s[i]):
            i -= 1
        return i + 1