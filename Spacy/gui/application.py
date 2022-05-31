import tkinter as tk
from tkinter import ttk
from appdirs import AppDirs
from spacy import load as get_pipe
from threading import Thread

from .widgets import Notebook, AddressBar
from .style import Style
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
        # Initialize style
        self.style = Style(self)

    def start(self):
        self.load_spacy_pipeline()
        self.mainloop()

    def load_spacy_pipeline(self, name:str='en_core_web_sm'):
        """Sets new attr to Root as pipeline"""
        def load():
            self.pipeline = get_pipe(name)
        # Load pipeline on a separate thread because it can
        # take a while.
        thread = Thread(target=load)
        thread.daemon = True
        thread.start()
