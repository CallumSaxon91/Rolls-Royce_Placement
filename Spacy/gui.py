import logging
import os
import tkinter as tk
from threading import Thread
from tkinter import filedialog, messagebox, ttk
from appdirs import AppDirs
from requests import ConnectionError as RequestsConnectionError

from cfg import ConfigManager
from exceptions import NotWikiPage
from process import get_data_from_url, parse_from_file, parse_string
from style import Style
from utils import image, open_new_file, export_to_csv

log = logging.getLogger(__name__)


class AppRoot(tk.Tk):
    def __init__(self, app_name:str, dirs:AppDirs, cfg:ConfigManager):
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
    in_search_state: bool = False
    
    def __init__(self, master):
        super().__init__(master, style='AddressBar.TFrame')
        self.settings = self.master.notebook.settings_frame
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
        fp = filedialog.askdirectory(mustexist=True)
        self.master.notebook.entities_frame.save(fp)

    def on_search_btn(self, event:tk.Event=None):
        def check_finished():
            if self.in_search_state:
                self.after(1000, check_finished)
                return                
            self.populate_fields(self.data)
            
        search_thread = Thread(target=self.search)
        search_thread.daemon = True
        search_thread.start()
        self.after(1000, check_finished)

    def search(self):
        self.in_search_state = True
        url = self.search_term.get()
        log.debug(f'starting search for: {url}')
        # update gui to reflect searching in progress
        self.update_gui_state(searching=True)
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
        except RequestsConnectionError:
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
        # update gui to show searching has finished
        self.update_gui_state(searching=False)
        # output results to gui and save to file
        if self.settings.quick_search.get():
            self.populate_fields(data)
        if self.settings.auto_save.get():
            self.master.notebook.entities_frame.save()
        self.data = data
        self.in_search_state = False

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
        self.master.notebook.entities_frame.populate_tree(data)
        log.debug('populated gui fields')


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
    """"""
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

    def save(self, fp:str=''):
        settings = self.master.settings_frame
        data = [
            self.tree.item(row)['values'] \
            for row in self.tree.get_children()
            ]
        if not fp: 
            fp = settings.auto_save_path.get()
        fp += '/output.csv'
        export_to_csv(data, fp)


class LegendFrame(ttk.Frame):
    """Contains widgets explaining spacy lingo stuff"""
    def __init__(self, master):
        super().__init__(master)
        self.master.add(self, text='Legend')
        
        entities = [
            ('PEOPLE', 'People, including fictional characters.'),
            ('NORP', 'Nationalities or religious or political groups.'),
            ('FAC', 'Buildings, airports, highways, bridges, etc.'),
            ('ORG', 'Companies, agencies, institutions, etc.'),
            ('LOC', 'Non-GPE locations, mountain ranges, bodies of water.'),
            ('PRODUCT', 'Objects, vehicles, foods, etc. (Not services.)'),
            ('EVENT', 'Named hurricanes, battles, wars, sports events, etc.'),
            ('WORK_OF_ART', 'Titles of books, songs, etc.'),
            ('LAW', 'Named documents made into laws.'),
            ('LANGUAGE', 'Any named language.'),
            ('DATE', 'Absolute or relative dates or periods.'),
            ('TIME', 'Times smaller than a day.'),
            ('PERCENT', 'Percentage, including ”%“.'),
            ('MONEY', 'Monetary values, including unit.'),
            ('QUANTITY', 'Measurements, as of weight or distance.'),
            ('ORDINAL', '“first”, “second”, etc.'),
            ('CARDINAL', 'Numerals that do not fall under another type.')
        ]
        for i, entity in enumerate(entities):
            ttk.Label(
                self, text=entity[0]
            ).grid(column=0, row=i)
            ttk.Label(
                self, text=entity[1]
            ).grid(column=1, row=i)


class SettingWidget(ttk.Frame):
    """Base widget for widgets in settings menu"""
    def __init__(
        self, master, label:str, desc:str, var:tk.Variable, **kw
        ):
        super().__init__(master, style='SettingWidget.TFrame', **kw)
        self.columnconfigure(0, weight=1)
        ttk.Label(
            self, text=label, style='SettingWidget.TLabel'
        ).grid(column=0, row=0, sticky='w', padx=(0, 5))
        ttk.Label(
            self, text=desc, style='SettingWidgetDesc.TLabel'
        ).grid(column=0, columnspan=2, row=2, sticky='w')
        var.trace_add('write', self.on_update)
        self.var = var
        
    def on_update(self, *args):
        cfg = self.master.master.master.master.cfg  # this is just bad
        cfg.update('settings', self.var)
        try:
            cfg.update('settings', self.var)
        except AttributeError:
            print('failed update attribute error')
            pass  # TODO: logging


class CheckBoxSetting(SettingWidget):
    """Setting with a checkbox. Best used with a boolean setting."""
    def __init__(
            self, master, label:str, desc:str, var:tk.Variable, **kw
        ):
        super().__init__(master, label, desc, var, **kw)
        ttk.Checkbutton(
            self, variable=var, style='SettingWidget.TCheckbutton'
        ).grid(column=1, row=0, sticky='w')


class TextSetting(SettingWidget):
    """Setting with a text box. Best used with a string setting"""
    def __init__(
        self, master, label:str, desc:str, var:tk.Variable, **kw
        ):
        super().__init__(master, label, desc, var, **kw)
        print(var, var.get())
        ttk.Entry(
            self, textvariable=var, style='SettingWidget.TEntry'
        ).grid(column=0, columnspan=2, row=1, sticky='we')


class SettingsFrame(ttk.Frame):
    """Contains setting controls"""
    def __init__(self, master):
        super().__init__(master)
        self.master.add(self, text='Settings')
        cfg: ConfigManager = self.master.master.cfg
        for name, setting in cfg.create_settings_vars():
            print('setattr', name, setting, setting.get())
            setattr(self, name, setting)
        frame = ttk.Frame(self)
        frame.pack(side='top', anchor='w')
        pack_info = {
            'fill': 'x', 'anchor': 'w', 'padx': 10, 'pady': 10
        }
        self.auto_save_checkbox = CheckBoxSetting(
            frame, label='Enable auto save',
            desc='Automatically save results to a file',
            var=self.auto_save
        )
        self.auto_save_checkbox.pack(pack_info)
        self.auto_save_path_entry = TextSetting(
            frame, label='Auto save path',
            desc='Where auto saved files are stored',
            var=self.auto_save_path
        )
        self.auto_save_path_entry.pack(pack_info)
        self.fast_search_checkbox = CheckBoxSetting(
            frame, label='Enable fast search',
            desc='Actively output results while searching (laggy)',
            var=self.quick_search
        )
        self.fast_search_checkbox.pack(pack_info)
