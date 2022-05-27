import os
import logging
import tkinter as tk
from appdirs import AppDirs

from cfg import ConfigManager
from gui.notebook import Notebook
from gui.addbar import AddressBar
from style import Style


log = logging.getLogger(__name__)


class AppRoot(tk.Tk):
    """Root of the application. Inherits from tkinter.Tk"""
    def __init__(self, app_name:str, dirs:AppDirs, cfg:ConfigManager):
        log.debug('Initializing main GUI window')
        super().__init__()
        self.app_name = app_name
        self.dirs = dirs
        self.cfg = cfg
        # setup root window
        self.title(app_name)
        self.geometry('700x400')
        self.iconbitmap(
            os.path.dirname(__file__) + r'\assets\icon.ico'
        )
        #self.resizable(False, False)
        # create and show controls
        self.notebook = Notebook(self)
        self.addbar = AddressBar(self)
        self.addbar.pack(fill='x')
        self.notebook.pack(fill='both', expand=True)
        # setup style
        # style must be setup after creating the controls because some
        # widgets can only be stylized after creation.
        self.style = Style(self)