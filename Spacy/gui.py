import logging
import os
import numpy as np
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
            self, master, img_fn:str, img_size:tuple[int, int], 
            style:str='TButton', **kw
        ):
        self.img = image(img_fn, img_size)
        super().__init__(
            master, image=self.img, cursor='hand2',
            style=style, **kw
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
        title = f'Wikipedia - {data["title"]}'
        self.master.notebook.results_tab.head_title.set(title)
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
    data: list[list]
    
    def __init__(self, master, headings, style='Treeview', anchor:str='w', **kw):
        log.debug(f'Creating custom treeview widget at {master}')
        super().__init__(master, **kw)
        # Create filter variables
        self.ent_filter_var = tk.StringVar()
        self.pos_filter_var = tk.StringVar()
        # Create treeview widget
        self.tree = ttk.Treeview(
            self, columns=headings, show='headings',
            style=style
        )
        self.tree.tag_configure(EVEN, background='gray90')
        self.tree.tag_configure(ODD, background='gray85')
        self.tree.pack(side='left', fill='both', expand=True)
        # Setup treeview headings
        for heading in headings:
            self.tree.column(heading, anchor=anchor, width=100)
            self.tree.heading(heading, text=heading.title())
        # Create scrollbar for treeview
        self.scroller = ttk.Scrollbar(master, command=self.tree.yview)
        self.tree.config(yscrollcommand=self.scroller.set)
        self.tree.bind('<Map>', self._pack_scroller)
        
        
    def _pack_scroller(self, *args, **kw):
        """pack treeview scrollbar"""
        # this is necessary instead of packing out right so that the 
        # scrollbar appears abover the tab header
        self.scroller.pack(side='right', fill='y', before=self)
        
    def create_filters(self, entities:list, pos:list):
        self.ent_filters = [
            'No Entity Filter', 'Entities Only', 'No Entities'
        ]
        self.ent_filters.extend(
            [f'{e.upper()} Only' for e in entities]
        )
        self.pos_filters = ['No POS Filter', 'POS Only', 'No POS']
        self.pos_filters.extend([f'{p.upper()} Only' for p in pos])
        self.ent_filter_var.set(self.ent_filters[0])
        self.pos_filter_var.set(self.pos_filters[0])
    
    def set_filter(self):
        ent_filter = self.ent_filter_var.get()
        pos_filter = self.pos_filter_var.get()
        ent_filter = ent_filter.removesuffix(' Only')
        pos_filter = pos_filter.removesuffix(' Only')
        # USE NUMPY ARRAY - TODO when back from work
        # https://www.geeksforgeeks.org/how-to-filter-two-dimensional-numpy-array-based-on-condition/
        data = np.array([
            self.tree.items(row)['values'] \
            for row in self.tree.get_children()
        ])
        self.insert_by_row(data)

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
    
    def tag(self, index:int) -> str:
        """
            Returns a str 'even' or 'odd' depending on if the provided 
            index is divisible by 2
        """
        return EVEN if index % 2 == 0 else ODD
    
    
class CustomMessageBox(tk.Toplevel):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.root: AppRoot = self.nametowidget('')
        # configure toplevel widget geometry
        w, h = 400, 250
        x, y = self.root.winfo_x(), self.root.winfo_y()
        x += int((self.root.winfo_width() / 2) - w / 2)
        y += int((self.root.winfo_height() / 2) - h / 2)
        self.geometry(f'{w}x{h}+{x}+{y}')
    
    def take_controls(self):
        # place toplevel above root and take controls
        self.transient(self.root)
        self.grab_set()
        self.root.wait_window(self)


class FilterMessageBox(CustomMessageBox):
    def __init__(self, data):
        super().__init__()
        # Create widgets
        headings = ('include', 'exclude')
        self.tree = CustomTreeView(
            self, headings, anchor='center',
            style='Selectable.Treeview'
        )
        self.tree.pack(fill='both', expand=True)
        # Populate treeview
        self.tree.insert_by_row(data)
        # Move button
        frame = ttk.Frame(self, style='Head.TFrame')
        frame.pack(side='bottom', fill='x')
        ttk.Button(
            self, text='Move', style='Head.TButton',
            command=self.on_move
        ).pack(side='left', padx=5, pady=5)
        ttk.Button(
            self, text='Move All', style='Head.TButton',
            command=self.on_move_all
        ).pack(side='left', pady=5)
        ttk.Button(
            self, text='Move All Others', style='Head.TButton',
            command=self.on_move_others
        ).pack(side='left', padx=5, pady=5)

    def on_move(self):
        tree = self.tree.tree
        # Find the selected row index
        focus = tree.focus()
        if not focus: return
        index = tree.index(focus)
        self.swap(focus, index)

    def on_move_all(self):
        tree = self.tree.tree
        for item in tree.get_children():
            index = tree.index(item)
            self.swap(item, index)

    def on_move_others(self):
        tree = self.tree.tree
        # Find the selected row index
        focus = tree.focus()
        if not focus: return
        for item in tree.get_children():
            if item == focus:
                continue
            index = tree.index(item)
            self.swap(item, index)
        
    def swap(self, focus, index):
        """Swap the selected row"""
        tree = self.tree.tree
        # Reverse the items in the row
        selected = tree.item(focus)['values']
        selected.reverse()
        # Replace old row with new row
        tree.delete(focus)
        tree.insert(
            '', index=index, values=selected, 
            tags=(self.tree.tag(index),)
        )
        # Update filter
        data = [
            self.tree.item(row)['values'] \
            for row in self.tree.get_children()
        ]
        data = tuple(zip(*data))
        self.root.notebook.results_tab.update_filter(data)


class Notebook(ttk.Notebook):
    """Tkinter frame that ouputs results from spacy"""
    def __init__(self, master:tk.Tk):
        log.debug('Initializing notebook')
        super().__init__(master)
        # Create notebook tabs
        self.results_tab = ResultsTab(self)
        self.legend_tab = LegendTab(self)
        self.settings_tab = SettingsTab(self)
        self.help_tab = HelpTab(self)
        # Show notebook tabs
        self.add(self.results_tab, text='Results')
        self.add(self.legend_tab, text='Legend')
        self.add(self.settings_tab, text='Settings')
        self.add(self.help_tab, text='Help')


class NotebookTab(ttk.Frame):
    def __init__(self, notebook, title:str, desc:str='', *args, **kw):
        super().__init__(notebook, *args, **kw)
        self.head_title = tk.StringVar(value=title)
        self.head_desc = tk.StringVar(value=desc)
        self.head = ttk.Frame(self, style='Head.TFrame')
        self.head.pack(side='top', fill='x')
        ttk.Label(
            self.head, style='HeadTitle.TLabel',
            textvariable=self.head_title
        ).pack(side='left', padx=5, pady=5)
        ttk.Label(
            self.head, style='Head.TLabel',
            textvariable=self.head_desc
        ).pack(side='left', padx=(0, 5), pady=5)


class ResultsTab(NotebookTab):
    """Tkinter ttk Frame containing output for parsed data"""
    include_filter: list = []
    exclude_filter: list = []

    def __init__(self, master):
        log.debug('Initializing results tab')
        super().__init__(master, title='Results')
        self.root = master.master
        self.include_filter.extend(list(self.root.cfg['entities']))
        self.include_filter.extend(list(self.root.cfg['POS_tags']))
        ImageButton(
            self.head, img_fn='filter.png', img_size=(18, 16),
            text='Filter Results', style='Compound.TButton',
            compound='right',
            command=self.show_filter_msgbox
        ).pack(side='right', padx=(5, 7), pady=5)
        self.tree = CustomTreeView(
            self, headings=('words', 'entity type', 'part of speech'),
            style='Selectable.Treeview'
        )
        self.tree.pack(
            side='bottom', fill='both', expand=True, before=self.head
        )

    def show_filter_msgbox(self):
        # zip wouldnt work? returned empty list? Doing this instead.
        data = []
        for n, i in enumerate(self.include_filter):
            try:
                data.append([i, self.exclude_filter[n]])
            except IndexError:
                data.append([i, ''])
        # Not happy with constructing the msgbox every time,
        # however the work around is painful and time consuming.
        # TODO: see above
        msgbox = FilterMessageBox(data=data)
        msgbox.take_controls()

    def update_filter(self, data:list[list]):
        self.include_filter = data[0]
        self.exclude_filter = data[1]
        tree = self.tree.tree
        data = []
        for item in tree.get_children():
            item = tree.item(item)['values']
            item = [str(i) for i in item]
            if any(i.lower() in self.exclude_filter for i in item):
                print('excluding', item)
                continue
            print('including', item)
            data.append(item)
        if data == []: return
        self.populate_tree(data)

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


class LegendTab(NotebookTab):
    """Contains widgets explaining spacy lingo stuff"""
    def __init__(self, master, title='Legend', desc=''):
        log.debug('Initializing legend tab')
        super().__init__(master, title='Legend',)
        self.tree = CustomTreeView(
            self, headings=('entities', '', 'parts of speech', '')
        )
        self.tree.pack(side='bottom', fill='both', expand=True, before=self.head)
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


class SettingsTab(NotebookTab):
    """Contains setting controls"""
    def __init__(self, master):
        log.debug('Initializing settings tab')
        super().__init__(master, title='Settings')
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
class HelpTab(NotebookTab):
    """Tab containing helpful info on how to use the app"""
    def __init__(self, master):
        log.debug('Initializing help tab')
        super().__init__(master, title='Help')
        test_btn = ttk.Button(
            self, text='www.weblink.com', style='HyperLink.TButton',
            cursor='hand2'
        )
        test_btn.pack()
        ttk.Label(self, text='testtext').pack()
