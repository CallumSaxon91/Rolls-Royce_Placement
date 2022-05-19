import os
import logging
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from appdirs import AppDirs
from threading import Thread
from requests import ConnectionError

from style import Style
from process import get_data_from_url, parse_string, parse_from_file
from exceptions import NotWikiPage
from utils import open_new_file, image


log = logging.getLogger(__name__)


class AppRoot(tk.Tk):
    def __init__(self, app_name:str, dirs:AppDirs):
        super().__init__()
        self.app_name = app_name
        self.dirs = dirs

        # setup root window
        self.title(app_name)
        self.geometry('700x400')
        self.iconbitmap(
            os.path.dirname(__file__) + r'\assets\icon.ico'
        )
        #self.resizable(False, False)

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


class ImageButton(ttk.Button):
    def __init__(
            self, master, img_fn:str, img_size:tuple[int, int], **kw
        ):
        self.img = image(img_fn, img_size)
        super().__init__(
            master, image=self.img, cursor='hand2', 
            style='AddressBarImg.TButton', **kw
        )


class AddressBar(ttk.Frame):
    """Tkinter frame that contains controls used to lookup web url"""
    def __init__(self, master):
        super().__init__(master, style='AddressBar.TFrame')
        self.search_term = tk.StringVar(
            value='https://en.wikipedia.org/wiki/'
        )
        self.search_btn = ttk.Button(
            self, text='Search', style='AddressBar.TButton',
            command=self.on_search_btn
        )
        self.search_btn.pack(side='left', fill='y', padx=5, pady=5)
        self.search_bar = ttk.Entry(
            self, style='AddressBar.TEntry',
            textvariable=self.search_term
        )
        self.search_bar.pack(
            side='left', fill='both',
            expand=True, pady=5
        )
        self.search_bar.bind('<Return>', self.on_search_btn)
        self.progress_bar = ttk.Progressbar(
            orient='horizontal',
            mode='indeterminate',
        )
        self.file_btn = ImageButton(
            self, img_fn='file.png', img_size=(20, 18), 
            command=self.on_file_btn
        )
        self.file_btn.pack(side='right', padx=5)
        sep = ttk.Separator(self, orient='vertical')
        sep.pack(side='right', before=self.file_btn, fill='y', pady=5)
        self.save_btn = ImageButton(
            self, img_fn='save.png', img_size=(20, 20), 
            command=self.on_save_btn
        )
        self.save_btn.pack(side='right', padx=5, before=sep)

    def on_file_btn(self):
        m = messagebox.askokcancel(
            title='Open File',
            message = 'You can use a text file as input data to ' \
                    'parse. The file can contain urls separated by ' \
                    ' a line break or a string of characters to be ' \
                    'parsed.'
        )
        if not m: return
        fp = filedialog.askopenfilename(
            filetypes=(('Text File', '*.txt'),)
        )
        self.search_term.set(fp)

    
    def on_save_btn(self):
        messagebox.showinfo(
            title='feature not added', 
            message='feature not added'
        )
        raise NotImplementedError

    def on_search_btn(self, event:tk.Event=None):
        search_thread = Thread(target=self.search)
        search_thread.daemon = True
        search_thread.start()

    def search(self):
        url = self.search_term.get()
        log.debug(f'starting search for: {url}')
        # update gui to reflect searching in progress
        self.update_gui_state(searching=True)
        try:
            data = get_data_from_url(self.search_term.get())
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
        
    def update_gui_state(self, searching:bool):
        """Enables or disables addressbar widgets"""
        if searching:
            self.progress_bar.pack(self.search_bar.pack_info())
            self.progress_bar.start(5)
            self.search_bar.pack_forget()
            self.search_btn.config(state='disabled')
            return
        self.search_bar.pack(self.progress_bar.pack_info())
        self.progress_bar.pack_forget()
        self.progress_bar.stop()
        self.search_btn.config(state='normal')
        
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
        self.settings_frame = SettingsFrame(self)


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
        

class SettingsFrame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master.add(self, text='Settings')
