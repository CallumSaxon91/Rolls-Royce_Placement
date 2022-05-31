import tkinter as tk
from tkinter import ttk
from appdirs import AppDirs

from .widgets import Notebook, AddressBar
from config import ConfigManager
from constants import ASSETS_PATH


class Root(tk.Tk):
    """Root of the GUI application"""
    def __init__(self, name:str, dirs:AppDirs, config:ConfigManager):
        super().__init__()
        self.dirs = dirs
        self.cfg = config(dirs)
        # Configure root window
        self.title(name)
        self.geometry('700x400')
        self.iconbitmap(f'{ASSETS_PATH}/icon.ico')
        # Create and show controls
        self.notebook = Notebook(self)
        self.addbar = AddressBar(self)
        self.addbar.pack(fill='x')
        self.notebook.pack(fill='both', expand=True)
        

    def start(self):
        self.mainloop()