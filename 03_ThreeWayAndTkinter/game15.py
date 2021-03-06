import random as rnd

import tkinter as tk
from tkinter import messagebox

class GameGrid:
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.numbers = list(range(w*h))
        self.buttons = []
        self.blank_coord = (rnd.randint(0,h-1), rnd.randint(0,w-1))
        #self.blank_coord = (3, 2)

    def shuffle_buttons(self):
        rnd.shuffle(self.buttons)

    def initialize_game_buttons(self, window):
        self.buttons = []
        for i in range(self.h):
            for j in range(self.w):
                n = self.numbers[i*self.w+j]
                if n != 0:
                    button = tk.Button(master=window,
                                    text=f"{n}".rjust(2," "),
                                    font="Arial 20")
                    def button_handler(game_grid=self, button=button):
                        playstep(game_grid, button)
                    button.configure(command=button_handler)
                    self.buttons.append(button)
        self.shuffle_buttons()

    def initialize_game_grid(self):
        bi = 0
        for i in range(self.h):
            for j in range(self.w):
                if self.blank_coord != (i,j):
                    self.buttons[bi].grid(row=i+1, column=j, sticky="WESN")
                    bi += 1
                    

def playstep(game_grid, button):
    info = button.grid_info()
    row,col = info["row"],info["column"]
    row -= 1 # shift according to window grid
    blank_row, blank_col = game_grid.blank_coord
    if (abs(blank_row-row) == 1 and abs(blank_col-col) == 0) or \
        (abs(blank_row-row) == 0 and abs(blank_col-col) == 1):
        button.grid(row=blank_row+1, column=blank_col, sticky="WESN")
        game_grid.blank_coord = (row,col)
    

def quit_game(game_state):
    game_state["over"] = True

def restart_game(gg, game_state):
    gg.shuffle_buttons()
    gg.blank_coord = (rnd.randint(0,gg.h-1), rnd.randint(0,gg.w-1))
    game_state["restart"] = True

def check_win_condition(gg):
    for b in gg.buttons:
        n = int(b.cget('text'))
    vis_numbers_order = list(map(lambda b:
                                int(b.cget('text'))-1, gg.buttons))
    pos_order = list(map(lambda b: (b.grid_info()['row']-1)*gg.w +
                                  b.grid_info()['column'], gg.buttons))
    #print("vis_numbers ", vis_numbers)
    #print("pos_order ", pos_order)
    return vis_numbers_order == pos_order


def main():
    window = tk.Tk()
    window.title("Game 15")
    window.geometry("+500+500")

    w,h = 4,4
    gg = GameGrid(w,h)
    game_state = {
        "over": False,
        "restart": True 
    }
    for i in range(1,h+1):
        window.rowconfigure(i, weight=1)
    for j in range(w):
        window.columnconfigure(j, weight=1)

    button = tk.Button(master=window, text=f"New",
                       font="Arial 18",
                       command=lambda: restart_game(gg, game_state))
    button.grid(row=0, column=0, columnspan=2)

    button = tk.Button(master=window, text=f"Exit",
                       font="Arial 18",
                       command=lambda: quit_game(game_state))
    button.grid(row=0, column=2, columnspan=2)

    gg.initialize_game_buttons(window)
    while not game_state["over"]:
        if game_state["restart"]:
            gg.initialize_game_grid()
            game_state["restart"] = False 
        window.update()
        if check_win_condition(gg):
            messagebox.showinfo(":)", "Congraz! You won!")
            restart_game(gg, game_state)
    window.destroy()

if __name__=="__main__":
   main() 
