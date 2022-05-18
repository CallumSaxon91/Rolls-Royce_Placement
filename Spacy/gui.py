import os
import logging
import tkinter as tk
from tkinter import ttk, messagebox
from appdirs import AppDirs
from threading import Thread
from PIL import Image, ImageTk
from requests import ConnectionError

from style import Style
from process import get_data_from_url, parse_string
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
        self.notebook = Notebook(self)
        self.notebook.pack(fill='both', expand=True)

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
        
    def update_gui_state(self, searching:bool):
        """Enables or disables addressbar widgets"""
        if searching:
            self.progress_bar.pack(self.search_bar.pack_info())
            self.progress_bar.start(20)
            self.search_bar.pack_forget()
            self.search_btn.config(state='disabled')
            return
        self.search_bar.pack(self.progress_bar.pack_info())
        self.progress_bar.pack_forget()
        self.progress_bar.stop()
        self.search_btn.config(state='normal')

    def search(self):
        """Search the web to find """
        url = self.search_term.get()
        log.debug(f'starting search for: {url}')
        # update gui to reflect searching in progress
        self.update_gui_state(searching=True)
        # attempt to get the data
        try:
            data = get_data_from_url(url)
        except NotWikiPage:
            log.error('cancelled search - entered url is invalid')
            self.update_gui_state(searching=False)
            messagebox.showerror(
                title='Search Cancelled',
                message='The URL entered does not lead to a ' \
                        'wikipedia article. Try Again.'
            )
            return
        except ConnectionError:
            log.error("couldn't establish connection with url")
            self.update_gui_state(searching=False)
            messagebox.showerror(
                title='Connection Error',
                message="Couldn't establish an internet connection. " \
                        "Please check your internet connection and " \
                        "try again."
            )
            return
        data = parse_string("".join(data['content']))
        # output results to gui and save to file
        self.populate_fields(data)
        self.save_results(data)
        # update gui to show searching has finished
        self.update_gui_state(searching=False)
        
    def populate_fields(self, data:list[tuple]):
        """output results to gui"""
        # results = self.master.results
        # results.entities_count.set(len(entities))
        # results.nouns_count.set(len(nouns))
        # results.verbs_count.set(len(verbs))
        # results.output.set('\n'.join(entities))
        self.master.notebook.entities_frame.populate_tree(data)
        log.debug('populated gui fields')

    def save_results(self, content:list[tuple]):
        return
        file = open_new_file(os.getcwd() + '/output')
        file.write('\n'.join(entities))
        file.close()
        log.debug('saved results to output file')

class Notebook(ttk.Notebook):
    """Tkinter frame that ouputs results from spacy"""
    def __init__(self, master:tk.Tk):
        super().__init__(master)
        self.entities_count = tk.IntVar()
        self.nouns_count = tk.IntVar()
        self.verbs_count = tk.IntVar()
        self.output = tk.StringVar()
        self.output.trace_add('write', lambda *_: self.insert_text())
        self.entities_frame = ResultsFrame(self)
        self.legend_frame = LegendFrame(self)


class ResultsFrame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        master.add(self, text='Results')
        headings = ('words', 'category', 'type')
        self.tree = ttk.Treeview(
            self, show='headings', columns=headings
        )
        self.tree.pack(side='left', fill='both', expand=True)
        for heading in headings:
            self.tree.column(heading, anchor='w')
            self.tree.heading(heading, text=heading.capitalize())
        scroller = ttk.Scrollbar(self, command=self.tree.yview)
        scroller.pack(side='right', fill='y')
        self.tree.config(yscrollcommand=scroller.set)
        self.tree.tag_configure('even', background='gray85')
        self.tree.tag_configure('odd', background='gray80')

    def populate_tree(self, content:list[list]):
        """populates tree from 2d array"""
        # self.tree.delete(*self.tree.winfo_children())
        self.tree.delete(*self.tree.get_children())
        for i, item in enumerate(content):
            tag = 'even' if i % 2 == 0 else 'odd'
            self.tree.insert('', 'end', values=item, tags=(tag,))
            

class LegendFrame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master.add(self, text='Legend')
