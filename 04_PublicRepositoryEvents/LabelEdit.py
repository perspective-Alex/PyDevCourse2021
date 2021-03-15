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

    def write(self, event):
        if event.char != "" and self.mode == CursorMode.INSERT:
            self.master.textvariable.set(
                self.master.textvariable.get() + event.char)

    def bind_events(self):
        self.bind_movement_left()
        self.bind_movement_right()
        self.bind_mode_switching_to_INSERT_or_writing()
        self.bind_mode_switching_to_COMMAND()
        self.bind_writing()
        self.bind_symbol_deletion()
    
    def bind_movement_left(self):
        def move_left(arg):
            new_x = int(self.place_info()['x']) - \
                self.width[CursorMode.COMMAND]
            if new_x >= 0:
                self.place_configure(x=new_x)
        self.bind("<Left>", move_left) 

    def bind_movement_right(self):
        def move_right(arg):
            new_x = int(self.place_info()['x']) + \
                self.width[CursorMode.COMMAND]
            if self.master.winfo_width() > \
                    (new_x + self.width[CursorMode.COMMAND]):
                self.place_configure(x=new_x)
        self.bind("<Right>", move_right) 

    def bind_mode_switching_to_INSERT_or_writing(self):
        def change_mode_or_write(arg):
            if self.mode == CursorMode.COMMAND:
                self.mode = CursorMode.INSERT
                self.place_configure(width=self.width[CursorMode.INSERT])
            else:
                self.write(arg)
        self.bind("i", change_mode_or_write, add=True)

    def bind_mode_switching_to_COMMAND(self):
        def change_mode_to_COMMAND(arg):
            if self.mode == CursorMode.INSERT:
                self.mode = CursorMode.COMMAND
                self.place_configure(width=self.width[CursorMode.COMMAND])
        self.bind("<Key-Escape>", change_mode_to_COMMAND)

    def bind_writing(self):
        self.bind("<Any-KeyPress>", self.write, add=True)

    def bind_symbol_deletion(self):
        def del_previous_symbol(arg):
            symb_i = int(self.place_info()['x']) // \
                self.width[CursorMode.COMMAND] 
            if symb_i > 0:
                text = self.master.textvariable.get()
                self.master.textvariable.set(text[:symb_i-1]+text[symb_i:])
                self.event_generate("<Left>")
        def del_next_symbol(arg):
            symb_i = int(self.place_info()['x']) // \
                self.width[CursorMode.COMMAND] 
            text = self.master.textvariable.get()
            if symb_i < len(text):
                self.master.textvariable.set(text[:symb_i]+text[symb_i+1:])

        self.bind("<BackSpace>", del_previous_symbol, add=False)
        self.bind("<Delete>", del_next_symbol, add=False)

class InputLabel(tk.Label):
    """tk.Entry behaviour imitation class"""
    def __init__(self, master, takefocus=True, highlightthickness=3, **kwargs):
        super().__init__(master, takefocus=takefocus,
                        highlightthickness=highlightthickness,
                        padx=0, pady=0,
                        **kwargs) 
        self.custom_cursor_text_variable = tk.StringVar()
        # this comment is to store service symbol "▯"
        self.font = kwargs['font']
        
        self.textvariable = kwargs["textvariable"]
        initial_text = kwargs["textvariable"].get()
        self.custom_cursor_text_variable.set(
                " " if initial_text == "" else initial_text[-1])

        character_width = self.font.actual(option='size')-6
        print(f"character width = {character_width}")
        self.custom_cursor = Cursor(self,
                             width=character_width,
                             textvariable=self.custom_cursor_text_variable,
                             font=self.font,
                             fg="brown",
                             relief=tk.RIDGE,
                             highlightbackground="green",
                             highlightthickness=1,
                             takefocus=True)
        self.custom_cursor.place(y=0, x=0, relheight=1)
        self.custom_cursor.bind_events()
        self.focus_set()
    


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
        #print(font_obj.actual(option="family"))
        print(font_obj.metrics())
        self.IL = InputLabel(self,
                            font=font_obj,
                            textvariable=self.S,
                            justify='left',
                            anchor='w')
        self.IL.grid(row=0, column=0, sticky="NEWS")


    def update(self):
        self.master.update()

    def mainloop(self):
        self.master.mainloop()

def dump(*args, **kwargs):
    print(*args, **kwargs)


app = App(title="Root window")
app.mainloop()
