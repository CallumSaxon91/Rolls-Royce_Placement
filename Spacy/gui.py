import os
import logging
import tkinter as tk
from tkinter import ttk, messagebox
from appdirs import AppDirs
from threading import Thread
from PIL import Image, ImageTk

from style import Style
from process import (
    get_data_from_url,
    get_ents_from_str,
    get_nouns_from_str,
    get_verbs_from_str
)
from exceptions import NotWikiPage, NoImageFound
from utils import open_new_file


log = logging.getLogger(__name__)
    
def image(filename:str, size:tuple[int, int]) -> ImageTk.PhotoImage:
    """returns PhotoImage object obtained from file path"""
    fp = 'assets/' + filename
    if not os.path.exists(fp):
        log.error(f'could not find image at fp: {fp}')
        raise NoImageFound
    im = Image.open(fp)
    im.resize(size, Image.ANTIALIAS)
    return ImageTk.PhotoImage(im)
    

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
        self.search_btn = ttk.Button(
            self, text='Search', style='AddressBar.TButton',
            command=self.on_search
        )
        self.search_btn.pack(side='left', fill='y', padx=5, pady=5)
        self.search_bar = ttk.Entry(
            self, style='AddressBar.TEntry',
            textvariable=self.search_term
        )
        self.search_bar.pack(
            side='left', fill='both',
            expand=True, padx=(0, 5), pady=5
        )
        self.search_bar.bind('<Return>', self.on_search)
        self.progress_bar = ttk.Progressbar(
            orient='horizontal',
            mode='indeterminate',
        )

    def on_search(self, event:tk.Event=None):
        search_thread = Thread(target=self.search)
        search_thread.daemon = True
        search_thread.start()

    def search(self):
        """Search the web to find """
        url = self.search_term.get()
        log.debug(f'starting search for: {url}')
        # update gui to reflect searching in progress
        self.progress_bar.pack(self.search_bar.pack_info())
        self.progress_bar.start(20)
        self.search_bar.pack_forget()
        self.search_btn.config(state='disabled')
        # attempt to get the data
        try:
            data = get_data_from_url(url)
        except NotWikiPage:
            messagebox.showerror(
                title='Search Cancelled',
                message='The URL entered does not lead ' \
                        'to a wikipedia article. Try Again.'
            )
            log.debug(
                'cancelled search because entered url is invalid'
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
        # update gui to show searching has finished
        self.search_bar.pack(self.progress_bar.pack_info())
        self.progress_bar.pack_forget()
        self.progress_bar.stop()
        self.search_btn.config(state='normal')
        
    def populate_fields(self, entities:list, nouns:list, verbs:list):
        """output results to gui"""
        results = self.master.results
        results.entities_count.set(len(entities))
        results.nouns_count.set(len(nouns))
        results.verbs_count.set(len(verbs))
        results.output.set('\n'.join(entities))
        log.debug('populated gui fields')

    def save_results(self, entities:list, nouns:list, verbs:list):
        file = open_new_file(os.getcwd() + '/output')
        file.write('\n'.join(entities))
        file.close()
        log.debug('saved results to output file')

class ResultsFrame(ttk.Notebook):
    """Tkinter frame that ouputs results from spacy"""
    def __init__(self, master:tk.Tk):
        super().__init__(master)
        self.entities_count = tk.IntVar()
        self.nouns_count = tk.IntVar()
        self.verbs_count = tk.IntVar()
        self.output = tk.StringVar()
        self.output.trace_add('write', lambda *_: self.insert_text())
        
        self.entities_frame = EntitiesFrame(self)
        

    def insert_text(self):
        self.output_widget.delete(1.0, 'end')
        self.output_widget.insert('insert', self.output.get())
        
        
class EntitiesFrame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        master.add(self, text='Entities')
        
class TreeFrame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        master.add(self, text='Entities Tree')
