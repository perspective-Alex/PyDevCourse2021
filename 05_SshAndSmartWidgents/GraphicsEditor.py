"""Module representing basic graphics editor"""

import tkinter as tk
from tkinter.font import Font as tkFont

class Application(tk.Frame):
    '''Sample tkinter application class'''

    def __init__(self, master=None, title="<application>", **kwargs):
        '''Create root window with frame, tune weight and resize'''
        super().__init__(master, **kwargs)
        self.master.title(title)
        self.master.geometry("+500+300")
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)
        self.grid(sticky="NEWS")
        self.create_widgets()
        self.bind_widgets()
        for column in range(self.grid_size()[0]):
            self.columnconfigure(column, weight=1)
        for row in range(self.grid_size()[1]):
            self.rowconfigure(row, weight=1)

    def create_widgets(self):
        '''Create all the widgets'''

    def bind_widgets(self):
        '''Bind events to the widgets'''


class OvalProperties:
    def __init__(self, canvas, oval_id):
        self.x0, self.y0, self.x1, self.y1 = canvas.coords(oval_id)
        self.border_width = canvas.itemcget(oval_id, "width")
        self.fill_color = canvas.itemcget(oval_id, "fill")
        self.border_color = canvas.itemcget(oval_id, "outline")
        self.oval_id = oval_id

    def __str__(self):
        return f"OVAL {self.oval_id} -> "\
                f"[coords:{self.x0},{self.y0},{self.x1},{self.y1} | "\
                f"border_width:{self.border_width} | "\
                f"fill_color:{self.fill_color} | "\
                f"border_color:{self.border_color}]\n"
    def __repr__(self):
        return self.__str__()


class App(Application):
    """Main application"""
    def set_font(self,size=20):
        return tkFont(family="fixed", size=size)
    def create_widgets(self):
        self.button_frame = tk.LabelFrame(self, text='Menu', font=self.set_font(14))
        self.button_frame.grid(row=1, column=0, sticky="NEWS")
        self.Q = tk.Button(self.button_frame, text="Quit", font=self.set_font(20),
                           command=self.master.quit)
        self.Q.grid(row=0,column=0)
        self.Upd = tk.Button(self.button_frame, text="Update canvas", font=self.set_font(20),
                             command=self.handle_changes)
        self.Upd.grid(row=0,column=1)

        self.workarea_frame = tk.LabelFrame(self, text='Draw & Watch', font=self.set_font(14))
        self.workarea_frame.grid(row=0, column=0, sticky="NEWS")
        self.T = tk.Text(self.workarea_frame, undo=True, wrap=tk.WORD, font=self.set_font(18),
                         inactiveselectbackground="MidnightBlue",
                         takefocus=False,
                         width=40)
        self.C = tk.Canvas(self.workarea_frame, bg='lavender', width="15c", height="15c")
        self.default_oval_width = 1
        self.default_oval_height = 1
        self.ovals = {}
        self.oval_creation = False
        self.oval_movement= False
        self.last_x, self.last_y = None, None
        self.description = None

        for O in [self.C, self.T]:
            O.grid(row=0, column=self.workarea_frame.grid_size()[1])

    def bind_widgets(self):
        self.C.bind("<Button-1>", lambda e: self.C.focus_set(), add=True)
        # self.C.bind("<Any-KeyPress>", print, add=True)
        self.bind_Canvas()
        self.bind_Text()

    def bind_Canvas(self):
        self.bind_oval()

    def bind_oval(self):
        def is_inside_oval(oval_id,x,y):
            x0,y0,x1,y1 = self.C.coords(oval_id)
            a = (x1-x0)/2
            b = (y1-y0)/2
            xc = x0 + a
            yc = y0 + b
            local_x = x - xc
            local_y = yc - y
            return ((local_x**2)/(a**2) + (local_y**2)/(b**2) - 1) <= 0

        def handle_press(event):
            i,inside = 0,False
            oval_ids = list(self.ovals.keys())
            while i < len(oval_ids) and not inside:
                inside = is_inside_oval(oval_ids[i], event.x, event.y)
                i += 1
            if not inside:
                # print(f"oval created, event:{event}")
                self.oval_creation = True
                oval_id = self.C.create_oval(event.x, event.y,
                                             event.x+self.default_oval_width,
                                             event.y+self.default_oval_height,
                                             fill='green',
                                             outline="midnightblue")
                self.ovals[oval_id] = OvalProperties(self.C, oval_id)
            elif inside:
                self.oval_movement = True
                self.last_x, self.last_y = event.x, event.y

        def handle_motion(event):
            if len(self.ovals) != 0:
                if self.oval_creation:
                    oval_id = sorted(self.ovals.keys())[-1]
                    x0,y0,x1,y1 = self.C.coords(oval_id)
                    scale_x = (event.x-x0) / (x1-x0)
                    scale_y = (event.y-y0) / (y1-y0)
                    if scale_x > 1.0 and scale_y > 1.0:
                        self.C.scale(oval_id, x0,y0, scale_x, scale_y)
                        _,_,x1,y1 = self.C.coords(oval_id)
                        self.ovals[oval_id].x1 = x1
                        self.ovals[oval_id].y1 = y1
                elif self.oval_movement:
                    oval_id = self.C.find_closest(event.x, event.y)[0]
                    if is_inside_oval(oval_id, event.x, event.y):
                        diff_x = event.x - self.last_x
                        diff_y = event.y - self.last_y
                        self.C.move(oval_id, diff_x, diff_y)
                        self.ovals[oval_id].x0 += diff_x
                        self.ovals[oval_id].x1 += diff_x
                        self.ovals[oval_id].y0 += diff_y
                        self.ovals[oval_id].y1 += diff_y

                    self.last_x = event.x
                    self.last_y = event.y

        def handle_release(event):
            self.oval_creation = False
            self.oval_movement = False
            self.describe_canvas()

        self.C.bind("<ButtonPress-1>", handle_press, add=True)
        self.C.bind("<Motion>", handle_motion, add=True)
        self.C.bind("<ButtonRelease-1>", handle_release, add=True)

    def describe_canvas(self):
        self.T.delete(1.0, tk.END)
        for oi, props in self.ovals.items():
            self.T.insert(tk.END, str(props))
        self.description = self.T.get(1.0, tk.END)

    def update_oval_properties(self, oval_id):
        props = self.ovals[oval_id]
        self.C.itemconfigure(oval_id,
                             width=props.border_width,
                             fill=props.fill_color,
                             outline=props.border_color)
        # print([props.x0, props.y0, props.x1, props.y1])
        x0,y0,x1,y1 = self.C.coords(oval_id)
        if [x0,y0,x1,y1] != [props.x0, props.y0, props.x1, props.y1]:
            scale_x = (props.x1 - props.x0) / (x1 - x0)
            scale_y = (props.y1 - props.y0) / (y1 - y0)
            self.C.scale(oval_id, x0, y0, scale_x, scale_y)
            x0, y0, x1, y1 = self.C.coords(oval_id)
            self.C.move(oval_id, props.x0-x0, props.y0-y0)
            # print(self.C.coords(oval_id))

    def draw_description(self):
        def handle_desc_line(line):
            oval_spec, prop_spec = line.strip('\n').split('->')
            oval_id = int(oval_spec.split(' ')[1])
            # print(f"{oval_id=}")
            oval_props = self.ovals[oval_id]
            for s_pr in prop_spec.strip(' ')[1:-1].split(" | "):
                name, val = s_pr.split(":")
                # print(f"{name=} {val=}")
                if name == 'coords':
                    oval_props.x0, oval_props.y0, oval_props.x1, oval_props.y1 = \
                        list(map(float,val.split(',')))
                else:
                    type = float if val.replace('.','').isnumeric() else str
                    if name not in oval_props.__dict__:
                        raise KeyError
                    oval_props.__dict__[name] = type(val)
            # print(f"{oval_props=}")
            return oval_id

        lines = self.T.get(1.0,tk.END).split('\n')
        # assert len(lines) == len(self.ovals), f"{len(lines)=} {len(self.ovals)=}"
        i = 0
        handled_oval_ids = []
        # print(lines)
        while i < len(lines):
            try:
                oval_id = handle_desc_line(lines[i])
                if oval_id in handled_oval_ids:
                    raise ValueError("Repeated oval_id in the description!")
                handled_oval_ids.append(oval_id)
                self.update_oval_properties(oval_id)
            except Exception as e:
                # print(e)
                # print(f'line {i}')
                self.T.tag_add("incorrect_line", f"{i+1}.0", f"{i+1}.end")
                self.T.tag_config("incorrect_line", background="orange red")
            else:
                self.T.tag_remove("incorrect_line", f"{i+1}.0", f"{i+1}.end")
            i += 1

    def handle_changes(self):
        if self.description != self.T.get(1.0,tk.END):
            self.draw_description()

    def bind_Text(self):
        def update_description(event):
            self.description = self.T.get(1.0, tk.END)
        self.T.bind("<Any-KeyPress>", update_description)


app = App(title="GraphicsEditor `Don't look at me like that`")
app.mainloop()
