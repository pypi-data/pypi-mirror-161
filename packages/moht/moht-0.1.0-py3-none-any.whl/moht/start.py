import tkinter as tk
from os import path

from moht.tk_gui import MohtTkGui


def run():
    """Function to start Mod Helper Tool GUI."""
    root = tk.Tk()
    width, height = 500, 200
    root.geometry(f'{width}x{height}')
    root.minsize(width=width, height=height)
    here = path.abspath(path.dirname(__file__))
    root.iconphoto(False, tk.PhotoImage(file=path.join(here, 'moht.png')))
    gui = MohtTkGui(master=root)
    gui.mainloop()


if __name__ == '__main__':
    run()
