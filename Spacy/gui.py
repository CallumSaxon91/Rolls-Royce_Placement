import logging
import tkinter as tk
from tkinter import ttk
from appdirs import AppDirs
from enum import Enum, auto

from style import Style
from process import get_data_from_url, get_ents_from_str


log = logging.getLogger(__name__)


class AppRoot(tk.Tk):
    def __init__(self, app_name:str, dirs:AppDirs):
        super().__init__()
        self.app_name = app_name
        self.dirs = dirs

        # setup root window
        self.title(app_name)
        self.geometry('700x400')
        self.resizable(False, False)

        # create and show controls
        self.addbar = AddressBar(self)
        self.addbar.pack(fill='x')
        ttk.Separator(self).pack(side='top', fill='x')
        self.results = ResultsFrame(self)
        self.results.pack(fill='both', expand=True)

        # setup style
        # style must be setup after creating the controls because some
        # widgets can only be stylized after creation.
        self.style = Style(self)

        log.debug('app root initialized')


class AddressBar(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, style='AddressBar.TFrame')
        self.search_term = tk.StringVar(value='www.google.com')
        search_btn = ttk.Button(
            self, text='Search', style='AddressBar.TButton',
            command=self.on_search
        )
        search_btn.pack(side='left', fill='y', padx=5, pady=5)
        search_bar = ttk.Entry(
            self, style='AddressBar.TEntry',
            textvariable=self.search_term
        )
        search_bar.pack(
            side='left', fill='both', 
            expand=True, padx=(0, 5), pady=5
        )

    def on_search(self, event:tk.Event=None):
        results_widget = self.master.results
        data = get_data_from_url(self.search_term.get())
        ents_as_list = [get_ents_from_str(s) for s in data['para']]
        ents = []
        for e in ents_as_list:
            ents.extend(e)
        
        [print(e) for e in ents]



class ResultsFrame(ttk.Frame):
    def __init__(self, master:tk.Tk):
        super().__init__(master)
        self.entities_count = tk.IntVar()

        ttk.Label(
            self, text='Entities:',
            style='Results.TLabel'
        ).grid(column=0, row=0)
        ttk.Label(
            self, style='Results.TLabel',
            textvariable=self.entities_count
        ).grid(column=1, row=0)
