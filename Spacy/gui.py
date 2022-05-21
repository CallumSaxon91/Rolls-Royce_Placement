import logging
import os
import tkinter as tk
from threading import Thread
from tkinter import filedialog, messagebox, ttk
from appdirs import AppDirs
from requests import ConnectionError as RequestsConnectionError

from cfg import ConfigManager
from exceptions import NotWikiPage
from process import get_data_from_url, parse_string
from style import Style
from utils import image, export_to_csv
from constants import EVEN, ODD

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


class ImageButton(ttk.Button):
    """ttk Button with an image"""
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
        log.debug('Initializing address bar widget')
        super().__init__(master, style='AddressBar.TFrame')
        self.settings = self.master.notebook.settings_tab
        self.search_term = tk.StringVar(
            value=self.settings.default_url.get()
        )
        # Search button
        self.search_btn = ttk.Button(
            self, text='Search', style='AddressBar.TButton',
            command=self.on_search_btn
        )
        self.search_btn.pack(side='left', fill='y', padx=5, pady=5)
        # Search bar aka address bar
        self.search_bar = ttk.Entry(
            self, style='AddressBar.TEntry',
            textvariable=self.search_term
        )
        self.search_bar.pack(
            side='left', fill='both', expand=True, pady=5
        )
        self.search_bar.bind('<Return>', self.on_search_btn)
        # Progress bar
        self.progress_bar = ttk.Progressbar(
            orient='horizontal',
            mode='indeterminate',
        )
        # Open file button
        self.file_btn = ImageButton(
            self, img_fn='file.png', img_size=(20, 18),
            command=self.on_file_btn
        )
        self.file_btn.pack(side='right', padx=5)
        sep = ttk.Separator(self, orient='vertical')
        # Save file button
        sep.pack(side='right', before=self.file_btn, fill='y', pady=5)
        self.save_btn = ImageButton(
            self, img_fn='save.png', img_size=(20, 20),
            command=self.on_save_btn
        )
        self.save_btn.pack(side='right', padx=5, before=sep)

    def on_file_btn(self):
        """File button has been clicked"""
        raise NotImplementedError('This feature has not been implemented yet')
        ok = messagebox.askokcancel(
            title='Open File',
            message = 'You can use a text file as input data to ' \
                    'parse. The file can contain urls separated by ' \
                    ' a line break or a string of characters to be ' \
                    'parsed.'
        )
        if not ok: return
        fp = filedialog.askopenfilename(
            filetypes=(('Text File', '*.txt'),)
        )
        self.search_term.set(fp)

    def on_save_btn(self):
        """Save button has been clicked"""
        fp = filedialog.askdirectory(mustexist=True)
        if not fp: return
        self.master.notebook.results_tab.save(fp)

    def on_search_btn(self, event:tk.Event=None):
        """Search button has been clicked"""
        def check_finished():
            if self.in_search_state:
                self.after(1000, check_finished)
                return
            self.populate_fields(self.data)
            if self.settings.auto_save.get():
                self.master.notebook.results_tab.save()

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
        except NotWikiPage:  # remove this exception to allow non-wikis
            log.error('cancelled search - entered url is invalid')
            self.update_gui_state(searching=False)
            messagebox.showerror(
                title='Search Cancelled',
                message='The URL entered does not lead to a ' \
                        'wikipedia article. Try Again.'
            )
            return
        except RequestsConnectionError:
            log.error(f"couldn't establish connection with {url}")
            self.update_gui_state(searching=False)
            messagebox.showerror(
                title='Connection Error',
                message="Couldn't establish an internet connection. " \
                        "Please check your internet connection and " \
                        "try again."
            )
            return
        # parse the data
        title = data['title']
        data = parse_string("".join(data['content']))
        # update gui to show searching has finished
        self.update_gui_state(searching=False)
        # set flag to inform app that the thread has finished
        self.data = data
        self.in_search_state = False
        log.debug('Search complete')

    def update_gui_state(self, searching:bool):
        """Enables or disables addressbar widgets"""
        log.debug(f'Updating address bar GUI. Disabled = {searching}')
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
        log.debug('Outputing parsed data')
        self.master.notebook.results_tab.populate_tree(data)


class CustomTreeView(ttk.Frame):
    """Tkinter ttk treeview with a scrollbar"""
    def __init__(self, master, headings, **kw):
        log.debug(f'Creating custom treeview widget at {master}')
        super().__init__(master, **kw)
        # Create treeview widget
        self.tree = ttk.Treeview(
            self, columns=headings, show='headings',
            style='Treeview'
        )
        self.tree.tag_configure(EVEN, background='gray85')
        self.tree.tag_configure(ODD, background='gray80')
        self.tree.pack(side='left', fill='both', expand=True)
        # Setup treeview headings
        for heading in headings:
            self.tree.column(heading, anchor='w', width=100)
            self.tree.heading(heading, text=heading.title())
        # Create scrollbar for treeview
        scroller = ttk.Scrollbar(self, command=self.tree.yview)
        scroller.pack(side='right', fill='y')
        self.tree.config(yscrollcommand=scroller.set)

    def insert_by_row(self, content:list[list]):
        for i, row in enumerate(content):
            tag = EVEN if i % 2 == 0 else ODD
            self.tree.insert('', 'end', values=row, tags=(tag,))

    def insert(self, *args, **kw):
        self.tree.insert(*args, **kw)

    def delete(self, *args, **kw):
        """delete data from treeview widget"""
        self.tree.delete(*args, **kw)

    def get_children(self, *args, **kw):
        """retrieve data from treeview widget"""
        return self.tree.get_children(*args, **kw)

    def item(self, *args, **kw):
        return self.tree.item(*args, **kw)


class Notebook(ttk.Notebook):
    """Tkinter frame that ouputs results from spacy"""
    def __init__(self, master:tk.Tk):
        log.debug('Initializing notebook')
        super().__init__(master)
        # Create notebook tabs
        self.results_tab = ResultsFrame(self)
        self.legend_tab = LegendFrame(self)
        self.settings_tab = SettingsFrame(self)
        self.help_tab = HelpFrame(self)
        # Register notebook tabs
        self.add(self.results_tab, text='Results')
        self.add(self.legend_tab, text='Legend')
        self.add(self.settings_tab, text='Settings')
        self.add(self.help_tab, text='Help')


class ResultsFrame(ttk.Frame):
    """Tkinter ttk Frame containing output for parsed data"""
    def __init__(self, master):
        log.debug('Initializing results tab')
        super().__init__(master)
        # Create data tree for output
        self.tree = CustomTreeView(
            self, headings=('words', 'entity type', 'part of speech')
        )
        self.tree.pack(fill='both', expand=True)

    def populate_tree(self, content:list[list]):
        """Output data to data tree"""
        self.tree.delete(*self.tree.get_children())
        self.tree.insert_by_row(content)

    def save(self, fp:str=''):
        """Save output to csv file"""
        log.debug('Exporting data to csv file')
        settings = self.master.settings_tab
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
        log.debug('Initializing legend tab')
        super().__init__(master)
        self.tree = CustomTreeView(
            self, headings=('entities', '', 'Part Of Speech', '')
        )
        self.tree.pack(fill='both', expand=True)
        # populate tree
        settings = master.master.cfg
        entities = settings['entities']
        word_classes = settings['POS_tags']
        for i, (entity, pos) in enumerate(
            zip(entities.items(), word_classes.items())
        ):
            tag = 'even' if i % 2 == 0 else 'odd'
            values = entity + pos
            values = [
                v.upper() if values.index(v) % 2 == 0 else v \
                for v in values
            ]
            self.tree.insert('', 'end', values=values, tags=(tag,))


class SettingWidget(ttk.Frame):
    """Base widget for widgets in settings menu"""
    def __init__(
        self, master, label:str, desc:str, var:tk.Variable, **kw
        ):
        log.debug(f'Initializing setting widget at {master}')
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
        log.debug(f'Updating setting widget {self}')
        cfg = self.master.master.master.master.cfg  # this is just bad
        cfg.update('settings', self.var)
        try:
            cfg.update('settings', self.var)
        except AttributeError:
            print('failed update attribute error')
            # TODO: logging


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
        ttk.Entry(
            self, textvariable=var, style='SettingWidget.TEntry'
        ).grid(column=0, columnspan=2, row=1, sticky='we')


class SettingsFrame(ttk.Frame):
    """Contains setting controls"""
    def __init__(self, master):
        log.debug('Initializing settings tab')
        super().__init__(master)
        # Load settings
        cfg: ConfigManager = self.master.master.cfg
        for name, setting in cfg.create_settings_vars():
            setattr(self, name, setting)
        # Setting widgets will be packed into this frame
        frame = ttk.Frame(self)
        frame.pack(side='top', anchor='w')
        pack_info = {
            'fill': 'x', 'anchor': 'w', 'padx': 10, 'pady': 10
        }
        # Create setting widgets
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
        self.default_url_entry = TextSetting(
            frame, label='Default URL',
            desc='URL in address bar on start up',
            var=self.default_url
        )
        self.default_url_entry.pack(pack_info)


# WIP
class HelpFrame(ttk.Frame):
    """Tab containing helpful info on how to use the app"""
    def __init__(self, master):
        log.debug('Initializing help tab')
        super().__init__(master)
        test_btn = ttk.Button(
            self, text='www.weblink.com', style='HyperLink.TButton',
            cursor='hand2'
        )
        test_btn.pack()
        ttk.Label(self, text='testtext').pack()
