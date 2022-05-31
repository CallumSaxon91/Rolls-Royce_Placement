import logging
import tkinter as tk
from tkinter import ttk
from appdirs import AppDirs
from spacy import load as get_pipe
from threading import Thread

from .widgets import Notebook, AddressBar
from .style import Style
from config import ConfigManager
from constants import ASSETS_PATH


log = logging.getLogger(__name__)


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
        """Start the GUI application"""
        self.load_spacy_pipeline(name='en_core_web_sm')
        self.mainloop()

    def load_spacy_pipeline(self, name):
        """Sets new attr to Root as pipeline"""
        log.debug('Loading spacy pipeline')
        def load():
            self.pipeline = get_pipe(name)
        # Load pipeline on a separate thread because it can
        # take a while.
        thread = Thread(target=load)
        thread.daemon = True
        thread.start()
