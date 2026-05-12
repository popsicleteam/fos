import sys


class Editor:
    def __init__(self, filename, width=80, height=24):
        self.filename = filename
        self.lines = []
        self.dirty = False
        self.cursor_x = 0
        self.cursor_y = 0
        self.scroll_offset = 0
        self.term_width = width
        self.term_height = height
        self.load()

    def load(self):
        try:
            with open(self.filename, "r") as f:
                lines = f.read().splitlines()
                self.lines = lines if lines else [""]
        except OSError:
            self.lines = [""]

    def save(self):
        try:
            with open(self.filename, "w") as f:
                for line in self.lines:
                    f.write(line + "\n")
            self.dirty = False
        except OSError as e:
            sys.stdout.write("\x1b[2J\x1b[H")
            print("Save error:", e)
            sys.stdout.write("\x1b[2J\x1b[H")

    def draw(self):
        """使用绝对定位重绘屏幕，避免滚动"""
        sys.stdout.write("\x1b[2J\x1b[H")  # 清屏，光标归位

        # 1. 状态行（第1行）
        status = f" {self.filename} {'*' if self.dirty else ' '} | Lines:{len(self.lines)} | Pos:{self.cursor_x + 1},{self.cursor_y + 1} | Ctrl+S:Save Ctrl+Q:Quit "
        if len(status) > self.term_width:
            status = status[: self.term_width - 1] + ">"
        sys.stdout.write(f"\x1b[1;1H{status}\x1b[K")

        content_height = self.term_height - 1

        # 滚动偏移修正
        if self.cursor_y < self.scroll_offset:
            self.scroll_offset = self.cursor_y
        elif self.cursor_y >= self.scroll_offset + content_height:
            self.scroll_offset = self.cursor_y - content_height + 1
        max_offset = max(0, len(self.lines) - content_height)
        if self.scroll_offset > max_offset:
            self.scroll_offset = max_offset
        if self.scroll_offset < 0:
            self.scroll_offset = 0

        # 2. 内容区域（第2行 ~ 第 term_height 行）
        for i in range(content_height):
            line_idx = self.scroll_offset + i
            sys.stdout.write(f"\x1b[{2 + i};1H")  # 移动到第 i 行内容起始
            if line_idx < len(self.lines):
                line = self.lines[line_idx]
                if len(line) > self.term_width:
                    display = line[: self.term_width - 1] + ">"
                else:
                    display = line
                sys.stdout.write(display)
            sys.stdout.write("\x1b[K")  # 清除该行剩余部分

        # 3. 移动光标到编辑位置
        screen_row = self.cursor_y - self.scroll_offset
        screen_col = min(self.cursor_x, self.term_width - 1)
        sys.stdout.write(f"\x1b[{screen_row + 2};{screen_col + 1}H")

    def insert_char(self, ch):
        row, col = self.cursor_y, self.cursor_x
        line = self.lines[row]
        self.lines[row] = line[:col] + ch + line[col:]
        self.cursor_x += 1
        self.dirty = True

    def insert_newline(self):
        row, col = self.cursor_y, self.cursor_x
        line = self.lines[row]
        self.lines[row] = line[:col]
        self.lines.insert(row + 1, line[col:])
        self.cursor_y += 1
        self.cursor_x = 0
        self.dirty = True

    def backspace(self):
        if self.cursor_x > 0:
            row = self.cursor_y
            line = self.lines[row]
            self.lines[row] = line[: self.cursor_x - 1] + line[self.cursor_x :]
            self.cursor_x -= 1
            self.dirty = True
        elif self.cursor_y > 0:
            prev_row = self.cursor_y - 1
            prev_line = self.lines[prev_row]
            curr_line = self.lines[self.cursor_y]
            self.lines[prev_row] = prev_line + curr_line
            del self.lines[self.cursor_y]
            self.cursor_y -= 1
            self.cursor_x = len(prev_line)
            self.dirty = True

    def delete(self):
        row, col = self.cursor_y, self.cursor_x
        if col < len(self.lines[row]):
            line = self.lines[row]
            self.lines[row] = line[:col] + line[col + 1 :]
            self.dirty = True
        elif row + 1 < len(self.lines):
            self.lines[row] += self.lines[row + 1]
            del self.lines[row + 1]
            self.dirty = True

    def move_cursor(self, dx, dy):
        new_x = self.cursor_x + dx
        new_y = self.cursor_y + dy
        new_y = max(0, min(new_y, len(self.lines) - 1))
        new_x = max(0, min(new_x, len(self.lines[new_y])))
        self.cursor_x = new_x
        self.cursor_y = new_y

    def run(self):
        self.draw()
        while True:
            c = sys.stdin.read(1)
            if not c:
                continue

            # 转义序列（方向键 / Home / End）
            if c == "\x1b":
                seq = sys.stdin.read(2)
                if seq == "[A":
                    self.move_cursor(0, -1)
                elif seq == "[B":
                    self.move_cursor(0, 1)
                elif seq == "[C":
                    self.move_cursor(1, 0)
                elif seq == "[D":
                    self.move_cursor(-1, 0)
                elif seq == "[H":
                    self.cursor_x = 0
                elif seq == "[F":
                    self.cursor_x = len(self.lines[self.cursor_y])
                self.draw()
                continue

            # 控制键
            if c == "\x13":  # Ctrl+S
                self.save()
                self.draw()
            elif c == "\x11":  # Ctrl+Q
                break
            elif c == "\x7f" or c == "\x08":  # Backspace
                self.backspace()
                self.draw()
            elif c == "\r" or c == "\n":  # Enter
                self.insert_newline()
                self.draw()
            elif c == "\t":  # Tab → 4 spaces
                self.insert_char("    ")
                self.draw()
            else:
                if 32 <= ord(c) < 127:  # 可打印 ASCII
                    self.insert_char(c)
                    self.draw()

        # 退出时清屏，恢复终端
        sys.stdout.write("\x1b[2J\x1b[H")


def edit(file, width=80, height=24):
    """
    文本编辑器入口函数
    :param file: 要编辑的文件名
    :param width: 终端宽度（列数），默认80
    :param height: 终端高度（行数），默认24
    """
    ed = Editor(file, width=width, height=height)
    ed.run()
