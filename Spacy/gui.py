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
            command=self.on_file_btn, style='AddressBarImg.TButton'
        )
        self.file_btn.pack(side='right', padx=5)
        sep = ttk.Separator(self, orient='vertical')
        # Save file button
        sep.pack(side='right', before=self.file_btn, fill='y', pady=5)
        self.save_btn = ImageButton(
            self, img_fn='save.png', img_size=(20, 20),
            command=self.on_save_btn, style='AddressBarImg.TButton'
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
        results_tab = self.master.notebook.results_tab
        results_tab.update_tree(data)
        results_tab.tree.unfiltered_data = data


class CustomTreeView(ttk.Treeview):
    """
        Custom tkinter ttk treeview with a scrollbar and methods for
        handling data.
    """
    # Data displayed in the tree
    data: list[list, list]
    filtered_data: list[list, list]
    # Filters
    hidden_ents: list = []
    hidden_pos: list = []
    
    def __init__(
        self, master:tk.Widget, headings:tuple[str],
        anchor:str='w', style:str='Treeview', 
        include_scrollbar:bool=True, **kw
    ):
        super().__init__(
            master, columns=headings, show='headings', style=style,
            **kw
        )
        log.debug(f'Constructing treeview widget: {self}')
        # Configure treeview
        self.tag_configure(EVEN, background='gray90')
        self.tag_configure(ODD, background='gray85')
        self._set_headings(headings, anchor)
        if include_scrollbar:
            self._build_scrollbar()
        
    def _build_scrollbar(self):
        """Build scrollbar for treeview"""
        self.scrollbar = ttk.Scrollbar(
            self.master, orient='vertical', command=self.yview
        )
        self.configure(yscrollcommand=self.scrollbar.set)
        # Pack the scrollbar after displaying the treeview
        def pack():
            self.scrollbar.pack(side='right', fill='y', before=self)
            self.unbind('<Map>')
        self.bind('<Map>', lambda e: pack())
        
    def _set_headings(self, headings:tuple, anchor:str):
        """Update the treeview headings"""
        self.configure(columns=headings)
        for heading in headings:
            self.column(heading, anchor=anchor, width=100)
            self.heading(heading, text=heading.title())
            
    def parity(self, integer:int) -> str:
        """Returns 'even' or 'odd' when given an integer"""
        return EVEN if integer % 2 == 0 else ODD
            
    def update_tree(self, data:list[list, list]):
        """Update the values in the treeview"""
        old_data = self.get_children()
        self.data = self.filter(data)
        self.filtered_data = self.filter(data)
        # If the data is identical to the previous data, don't bother
        # updating the widget with the new data.
        if self.filtered_data == list(old_data):
            log.debug(
                'Data has not changed while updating treeview ' /
                f'{self}. Skipping population of treeview.'
            )
            return
        log.debug(f'Populating treeview {self}')
        # Insert new data into treeview widget
        self.delete(*old_data)
        for i, row in enumerate(data):
            tag = self.parity(i)
            self.insert('', 'end', values=row, tags=(tag,))
        log.debug(
            f'Finished populating treeview {self} with {i} widgets'
        )

    def filter(self, data:list[list, list]):
        """Filter out data"""
        hidden = self.hidden_ents.copy()
        hidden.extend(self.hidden_pos)
        for i, row in enumerate(data):
            if any(item.lower() in hidden for item in row):
                log.debug(
                    f'Removing row {row} because it contains a ' \
                    'filtered item'
                )
                data.pop(i)
        return data
    
    def set_filter(
        self, hidden_ents:list, hidden_pos:list, update:bool
    ):
        self.hidden_ents = hidden_ents
        self.hidden_pos = hidden_pos
        if update:
            self.update_tree(data=self.data)


class CustomMessageBox(tk.Toplevel):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.root: AppRoot = self.nametowidget('')
        # # configure toplevel widget geometry
        # w, h = 400, 250
        x, y = self.root.winfo_x(), self.root.winfo_y()
        # x += int((self.root.winfo_width() / 2) - w / 2)
        # y += int((self.root.winfo_height() / 2) - h / 2)
        self.geometry(f'+{x}+{y}')
    
    def take_controls(self):
        # place toplevel above root and take controls
        self.transient(self.root)
        self.grab_set()
        self.root.wait_window(self)


class FilterMessageBox(CustomMessageBox):
    def __init__(self):
        super().__init__()
        # Collect data
        self.results_tab = self.root.notebook.results_tab
        self.entities = self.root.cfg['entities']
        self.pos = self.root.cfg['POS_tags']
        self.hidden_ents = self.results_tab.tree.hidden_ents
        self.hidden_pos = self.results_tab.tree.hidden_pos
        # Create widgets
        notebook = ttk.Notebook(self)
        notebook.pack(fill='both', expand=True)
        ents_tab = FilterMessageBoxTab(notebook, title='Entities')
        pos_tab = FilterMessageBoxTab(
            notebook, title='Parts Of Speech'
        )
        notebook.add(ents_tab, text='Entities') # repeats bad
        notebook.add(pos_tab, text='Parts Of Speech')
        # Populate trees
        ents_tab.tree.update_tree(
            data=self._sort_data(self.entities, self.hidden_ents)
        )
        pos_tab.tree.update_tree(
            data=self._sort_data(self.pos, self.hidden_pos)
        )
        
    def _sort_data(self, data:list, hidden:list) -> list[list, list]:
        result = []
        for i in data:
            if i in hidden:
                result.append(['', i.upper()])
                continue
            result.append([i.upper(), ''])
        return result



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
        

class FilterMessageBoxTab(NotebookTab):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.tree = CustomTreeView(
            self, headings=('include', 'exlude'), anchor='w',
            style='Selectable.Treeview'
        )
        self.tree.pack(fill='both', expand=True)
        ttk.Separator(self, orient='horizontal').pack(fill='x')
        control_panel = ttk.Frame(self, style='Head.TFrame')
        control_panel.pack(side='bottom', fill='x')
        ttk.Button(
            self, text='Move Selected', style='Head.TButton',
            command=self.move_selected
        ).pack(side='left', padx=10, pady=10)
        ttk.Button(
            self, text='Move Not Selected', style='Head.TButton',
            command=None
        ).pack(side='left', padx=(0, 10), pady=10)
        ttk.Button(
            self, text='Move All', style='Head.TButton',
            command=self.move_all
        ).pack(side='left', padx=(0, 10), pady=10)
        ttk.Checkbutton(
            self, text='  Exclude All', style='Head.TCheckbutton'
        ).pack(side='right', padx=10, pady=10)
        
    def move(self, focus:str):
        values = self.tree.item(focus)['values']
        if not values: return
        values.reverse()
        index = self.tree.index(focus)
        self.tree.delete(focus)
        new = self.tree.insert(
            '', index, values=values, tags=(self.tree.parity(index),)
        )
        # Set focus on the changed row
        self.tree.focus(new)
        self.tree.selection_set(new)
        
    def move_selected(self):
        self.move(self.tree.focus())
        
    def move_all(self):
        for item in self.tree.get_children():
            self.move(item)
       

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


class ResultsTab(NotebookTab):
    """Tkinter ttk Frame containing output for parsed data"""
    def __init__(self, master):
        log.debug('Initializing results tab')
        super().__init__(master, title='Results')
        self.root = master.master
        # Create filter button widget
        ImageButton(
            self.head, img_fn='filter.png', img_size=(18, 16),
            text='Filter Results', style='Compound.TButton',
            compound='right', command=self.show_filter_msgbox
        ).pack(side='right', padx=(5, 7), pady=5)
        # Create treeview widget
        self.tree = CustomTreeView(
            self, style='Selectable.Treeview', 
            headings=('words', 'entity type', 'part of speech')
        )
        self.tree.pack(
            side='bottom', fill='both', expand=True, before=self.head
        )
        # TODO: could edit this to use a save from the config file
        self.tree.set_filter(
            hidden_ents=[], hidden_pos=[], update=False
        )

    def show_filter_msgbox(self):
        # Not happy with constructing the msgbox every time,
        # however the work around is painful and time consuming.
        # TODO: see above
        msgbox = FilterMessageBox()
        msgbox.take_controls()

    def update_tree(self, data:list[list]):
        """Update treeview with new data"""
        self.tree.update_tree(data=data)

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
