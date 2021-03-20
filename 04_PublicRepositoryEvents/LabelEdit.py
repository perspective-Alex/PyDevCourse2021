"""Module representing custom Label class which imitates tkinter.Entry behaviour"""
import tkinter as tk
from tkinter import font as tkFont
from enum import Enum


class CursorMode(Enum):
    INSERT = 0
    COMMAND = 1


class Cursor(tk.Label):
    """Custom cursor inside InputLabel object"""
    def __init__(self, master, width, **kwargs):
        super().__init__(master, **kwargs)
        self.mode = CursorMode.COMMAND
        self.width = {
            CursorMode.INSERT: 2,
            CursorMode.COMMAND: width
        }
        self.char_width = self.width[CursorMode.COMMAND]

    def set_current_symbol(self, text):
        if self.mode == CursorMode.COMMAND:
            symb_i = int(self.place_info()['x']) // self.char_width
            self.configure(text=text[symb_i])

    def bind_events(self):
        self.bind_movements()

    def bind_movements(self):
        self.bind_movement_left()
        self.bind_movement_right()
        self.bind_Home_End_movement()

    def bind_movement_left(self):
        def move_left(arg):
            new_x = int(self.place_info()['x']) - \
                self.width[CursorMode.COMMAND]
            if new_x >= 0:
                self.place_configure(x=new_x)
                text = self.master.textvariable.get()
                self.set_current_symbol(text)
        self.bind("<Left>", move_left)

    def bind_movement_right(self):
        def move_right(arg):
            text = self.master.textvariable.get()
            cur_x = int(self.place_info()['x'])
            right_border = len(text)*self.char_width if self.mode == \
                CursorMode.INSERT else (len(text)-1)*self.char_width
            if text != '' and cur_x < right_border:
                new_x = cur_x + \
                    self.width[CursorMode.COMMAND]
                if self.master.winfo_width() > \
                    (new_x + (self.width[self.mode]
                     if self.mode == CursorMode.COMMAND else 0)):
                    self.place_configure(x=new_x)
                    self.set_current_symbol(text)
        self.bind("<Right>", move_right)

    def bind_Home_End_movement(self):
        def move_end(arg):
            text = self.master.textvariable.get()
            if self.mode == CursorMode.INSERT:
                new_x = self.char_width * len(text)
                self.place_configure(x=new_x)
            else:
                new_x = 0 if len(text) == 0 else \
                    self.char_width * (len(text)-1)
                self.place_configure(x=new_x)
                self.set_current_symbol(text)

        def move_home(arg):
            self.place_configure(x=0)
            text = self.master.textvariable.get()
            self.set_current_symbol(text)

        self.bind("<End>", move_end)
        self.bind("<Home>", move_home)


class InputLabel(tk.Label):
    """tk.Entry behaviour imitation class"""
    def __init__(self, master, takefocus=True, highlightthickness=3, **kwargs):
        super().__init__(master, takefocus=takefocus,
                         highlightthickness=highlightthickness,
                         padx=0, pady=0,
                         **kwargs)
        # this comment is to store service symbol "▯"
        self.font = kwargs['font']

        self.textvariable = kwargs["textvariable"]
        initial_text = kwargs["textvariable"].get()

        # set pixel length of any char with such a font
        self.char_width = self.font.measure('s')
        self.custom_cursor = Cursor(self,
                                    width=self.char_width,
                                    text="",
                                    font=self.font,
                                    bg="yellow",
                                    fg="brown",
                                    relief=tk.GROOVE,
                                    highlightbackground="green",
                                    highlightthickness=0,
                                    takefocus=False)
        self.custom_cursor.place(y=0, x=0, width=self.char_width, relheight=1)
        self.bind_events()

    def write(self, event):
        if event.char != "" and self.custom_cursor.mode == CursorMode.INSERT:
            symb_i = int(self.custom_cursor.place_info()['x']) // \
                self.custom_cursor.width[CursorMode.COMMAND]
            text = self.textvariable.get()
            self.textvariable.set(
                 text[:symb_i] + event.char + text[symb_i:])
            self.update()
            self.custom_cursor.event_generate("<Right>")

    def bind_events(self):
        self.custom_cursor.bind_events()
        self.bind_movements()
        self.bind_mode_switching_to_INSERT_or_writing()
        self.bind_mode_switching_to_COMMAND()
        self.bind_writing()
        self.bind_symbol_deletion()
        self.bind_mouse()

    def bind_movements(self):
        for event in ["<Left>", "<Right>", "<End>", "<Home>"]:
            def handler(arg, event=event):
                self.custom_cursor.focus_set()
                self.event_generate(event)
                self.focus_set()
            self.bind(event, handler)

    def bind_mode_switching_to_INSERT_or_writing(self):
        def change_mode_or_write(arg, key):
            if self.custom_cursor.mode == CursorMode.COMMAND:
                self.custom_cursor.mode = CursorMode.INSERT
                self.custom_cursor.place_configure(
                    width=self.custom_cursor.width[CursorMode.INSERT])
                self.custom_cursor.configure(highlightthickness=1)
                if key == 'a':
                    self.custom_cursor.event_generate("<Right>")
            else:
                self.write(arg)
        self.bind("i", lambda arg: change_mode_or_write(arg, "i"), add=True)
        self.bind("a", lambda arg: change_mode_or_write(arg, "a"), add=True)

    def bind_mode_switching_to_COMMAND(self):
        def change_mode_to_COMMAND(arg):
            if self.custom_cursor.mode == CursorMode.INSERT:
                self.custom_cursor.mode = CursorMode.COMMAND
                self.custom_cursor.place_configure(
                    width=self.custom_cursor.width[CursorMode.COMMAND])
                self.custom_cursor.configure(highlightthickness=0)
                symb_i = int(self.custom_cursor.place_info()['x']) // \
                    self.custom_cursor.width[CursorMode.COMMAND]
                text = self.textvariable.get()
                if text == "":
                    self.custom_cursor.configure(text=" ")
                elif symb_i < len(text):
                    self.custom_cursor.configure(text=f"{text[symb_i]}")
                elif symb_i == len(text):
                    self.custom_cursor.event_generate("<Left>")
        self.bind("<Key-Escape>", change_mode_to_COMMAND)

    def bind_writing(self):
        self.bind("<Any-KeyPress>", self.write, add=True)

    def bind_symbol_deletion(self):
        def del_previous_symbol(arg):
            if self.custom_cursor.mode == CursorMode.INSERT:
                symb_i = int(self.custom_cursor.place_info()['x']) // \
                    self.custom_cursor.width[CursorMode.COMMAND]
                if symb_i > 0:
                    text = self.textvariable.get()
                    self.textvariable.set(text[:symb_i-1]+text[symb_i:])
                    self.custom_cursor.event_generate("<Left>")

        def del_next_symbol(arg):
            if self.custom_cursor.mode == CursorMode.INSERT:
                symb_i = int(self.custom_cursor.place_info()['x']) // \
                    self.custom_cursor.width[CursorMode.COMMAND]
                text = self.textvariable.get()
                if symb_i < len(text):
                    self.textvariable.set(text[:symb_i]+text[symb_i+1:])

        self.bind("<BackSpace>", del_previous_symbol, add=False)
        self.bind("<Delete>", del_next_symbol, add=False)

    def bind_mouse(self):
        def capture_focus_and_pose_cursor(arg):
            text = self.textvariable.get()
            if text != "":
                new_x = arg.x - (arg.x % self.char_width)
                right_border = len(text)*self.char_width \
                    if self.custom_cursor.mode == CursorMode.INSERT else \
                    (len(text)-1)*self.char_width
                if new_x > right_border:
                    new_x = right_border
                self.custom_cursor.place_configure(x=new_x)
                self.custom_cursor.set_current_symbol(text)
            self.focus_set()

        self.bind("<Button-1>", capture_focus_and_pose_cursor, add=False)


class App(tk.Frame):
    """Main application"""
    def __init__(self, master=None, title="App", **kwargs):
        super().__init__(master, **kwargs)
        self.master.title(title)
        self.master.geometry("+500+300")
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)
        self.master.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.grid(sticky="NEWS")
        font_obj = tkFont.Font(family="fixed", size=20)

        self.B1 = tk.Button(self, font=font_obj,
                            text="Quit", command=self.master.quit)
        self.B1.grid(row=1, column=0, sticky="NEWS")

        self.S = tk.StringVar()
        self.S.set("")
        self.IL = InputLabel(self,
                             font=font_obj,
                             textvariable=self.S,
                             justify='left',
                             anchor='w')
        self.IL.grid(row=0, column=0, sticky="NEWS")
        self.IL.focus_set()

    def update(self):
        self.master.update()

    def mainloop(self):
        self.master.mainloop()


app = App(title="VIMish text editor emulator")
app.mainloop()
