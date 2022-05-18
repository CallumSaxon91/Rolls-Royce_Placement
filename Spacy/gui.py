import logging
import tkinter as tk
from tkinter import ttk, messagebox
from appdirs import AppDirs

from style import Style
from process import (
    get_data_from_url, 
    get_ents_from_str,
    get_nouns_from_str,
    get_verbs_from_str,
    get_person_from_str,
    get_date_from_str,
    get_organisations_from_str,
)
from exceptions import NotWikiPage


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
        results_widget = self.master.results
        try:
            data = get_data_from_url(self.search_term.get())
        except NotWikiPage:
            messagebox.showerror(
                title='Error',
                message='The URL entered does not lead ' \
                        'to a wikipedia article. Try Again.'
            )
            return
        ents_as_list = [get_ents_from_str(s) for s in data['para']]
        ents = []
        for e in ents_as_list:
            ents.extend(e)
        
        nouns_as_list = [get_nouns_from_str(s) for s in data['para']]
        nouns = []
        for n in nouns_as_list:
            nouns.extend(n)
            
        verbs_as_list = [get_verbs_from_str(s) for s in data['para']]
        verbs = []
        for n in verbs_as_list:
            verbs.extend(n)

        persons_as_list = [get_person_from_str(s) for s in data['para']]
        persons = []
        for n in persons_as_list:
            persons.extend(n)
        
        dates_as_list = [get_date_from_str(s) for s in data['para']]
        dates = []
        for n in dates_as_list:
            dates.extend(n)

        organisations_as_list = [get_organisations_from_str(s) for s in data['para']]
        organisations = []
        for n in organisations_as_list:
            organisations.extend(n)
        
        results_widget.entities_count.set(len(ents))
        results_widget.nouns_count.set(len(nouns))
        results_widget.verbs_count.set(len(verbs))
        results_widget.persons_count.set(len(persons))
        results_widget.dates_count.set(len(dates))
        results_widget.organisations_count.set(len(organisations))
        results_widget.output.set('\n'.join(ents))


class ResultsFrame(ttk.Frame):
    def __init__(self, master:tk.Tk):
        super().__init__(master)
        self.entities_count = tk.IntVar()
        self.nouns_count = tk.IntVar()
        self.verbs_count = tk.IntVar()
        self.persons_count = tk.IntVar()
        self.dates_count = tk.IntVar()
        self.organisations_count = tk.IntVar()
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
        ).grid(column=1, row=0, padx=20)
        ttk.Label(
            counts_frame, style='Results.TLabel',
            textvariable=self.nouns_count
        ).grid(column=1, row=1, padx=20)
        
        # verbs counter
        ttk.Label(
            counts_frame, text='Verbs:',
            style='Results.TLabel'
        ).grid(column=2, row=0)
        ttk.Label(
            counts_frame, style='Results.TLabel',
            textvariable=self.verbs_count
        ).grid(column=2, row=1)

        # persons counter
        ttk.Label(
            counts_frame, text='People:',
            style='Results.TLabel'
        ).grid(column=4, row=0, padx=20)
        ttk.Label(
            counts_frame, style='Results.TLabel',
            textvariable=self.persons_count
        ).grid(column=4, row=1, padx=20)

        # dates counter
        ttk.Label(
            counts_frame, text='Dates:',
            style='Results.TLabel'
        ).grid(column=5, row=0)
        ttk.Label(
            counts_frame, style='Results.TLabel',
            textvariable=self.dates_count
        ).grid(column=5, row=1)

        # organisations counter
        ttk.Label(
            counts_frame, text='Organisations:',
            style='Results.TLabel'
        ).grid(column=6, row=0, padx=20)
        ttk.Label(
            counts_frame, style='Results.TLabel',
            textvariable=self.organisations_count
        ).grid(column=6, row=1, padx=20)
        
        self.output_widget = tk.Text(self)
        self.output_widget.pack(side='top', padx=10, pady=(0, 10))
        
        scroller = ttk.Scrollbar(
            master, orient='vertical', 
            command=self.output_widget.yview
        )
        scroller.pack(side='right', fill='y')
        self.output_widget.config(yscrollcommand=scroller.set)
        
    def insert_text(self):
        self.output_widget.delete(1.0, 'end')
        self.output_widget.insert('insert', self.output.get())