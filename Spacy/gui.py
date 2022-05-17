import os
import logging
import tkinter as tk
from tkinter import ttk, messagebox
from appdirs import AppDirs
from threading import Thread

from style import Style
from process import (
    get_data_from_url,
    get_ents_from_str,
    get_nouns_from_str,
    get_verbs_from_str
)
from exceptions import NotWikiPage
from utils import open_new_file


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
    """Tkinter frame that contains controls used to lookup web url"""
    def __init__(self, master):
        super().__init__(master, style='AddressBar.TFrame')
        self.search_term = tk.StringVar(
            value='https://en.wikipedia.org/wiki/'
        )
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
        search_bar.bind('<Return>', self.on_search)

    def on_search(self, event:tk.Event=None):
        search_thread = Thread(target=self.search)
        search_thread.daemon = True
        search_thread.start()

    def search(self):
        """Search the web to find """
        
        try:
            data = get_data_from_url(self.search_term.get())
        except NotWikiPage:
            messagebox.showerror(
                title='Error',
                message='The URL entered does not lead ' \
                        'to a wikipedia article. Try Again.'
            )
            return
        def get_data_from_para(func) -> list:
            """use to get data from entities"""
            entities = [func(s) for s in data['para']]
            result = []
            for entity in entities:
                result.extend(entity)
            return result
        # get lists of various data from collected paragraphs
        ents = get_data_from_para(get_ents_from_str)
        nouns = get_data_from_para(get_nouns_from_str)
        verbs = get_data_from_para(get_verbs_from_str)
        # output results to gui
        self.populate_fields(ents, nouns, verbs)
        # write results to output file
        self.save_results(ents, nouns, verbs)
        
    def populate_fields(self, entities:list, nouns:list, verbs:list):
        """output results to gui"""
        results = self.master.results
        results.entities_count.set(len(entities))
        results.nouns_count.set(len(nouns))
        results.verbs_count.set(len(verbs))
        results.output.set('\n'.join(entities))

    def save_results(self, entities:list, nouns:list, verbs:list):
        file = open_new_file(os.getcwd() + '/output')
        file.write('\n'.join(entities))
        file.close()

class ResultsFrame(ttk.Frame):
    """Tkinter frame that ouputs results from spacy"""
    def __init__(self, master:tk.Tk):
        super().__init__(master)
        self.entities_count = tk.IntVar()
        self.nouns_count = tk.IntVar()
        self.verbs_count = tk.IntVar()
        self.output = tk.StringVar()
        self.output.trace_add('write', lambda *_: self.insert_text())

        counts_frame = ttk.Frame(self)
        counts_frame.pack(side='top', pady=5)
        # entities counter
        ttk.Label(
            counts_frame, text='Entities:',
            style='Results.TLabel'
        ).grid(column=0, row=0)
        ttk.Label(
            counts_frame, style='Results.TLabel',
            textvariable=self.entities_count
        ).grid(column=0, row=1)
        # nouns counter
        ttk.Label(
            counts_frame, text='Nouns:',
            style='Results.TLabel'
        ).grid(column=1, row=0, padx=10)
        ttk.Label(
            counts_frame, style='Results.TLabel',
            textvariable=self.nouns_count
        ).grid(column=1, row=1, padx=10)
        # verbs counter
        ttk.Label(
            counts_frame, text='Verbs:',
            style='Results.TLabel'
        ).grid(column=2, row=0)
        ttk.Label(
            counts_frame, style='Results.TLabel',
            textvariable=self.verbs_count
        ).grid(column=2, row=1)
        # text box for output
        self.output_widget = tk.Text(self)
        self.output_widget.pack(side='top', padx=10, pady=(0, 10))
        # scrollbar for output widget
        scroller = ttk.Scrollbar(
            master, orient='vertical',
            command=self.output_widget.yview
        )
        scroller.pack(side='right', fill='y')
        self.output_widget.config(yscrollcommand=scroller.set)

    def insert_text(self):
        self.output_widget.delete(1.0, 'end')
        self.output_widget.insert('insert', self.output.get())
