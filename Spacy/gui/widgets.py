import logging
import tkinter as tk
from tkinter import ttk

from utils import image, up_list
from constants import ODD, EVEN


log = logging.getLogger(__name__)


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

    def __init__(self, master):
        log.debug('Initializing address bar widget')
        super().__init__(master, style='AddressBar.TFrame')
        self.settings = self.master.notebook.settings_tab
        # Begin parsing process button
        self.begin_btn = ttk.Button(
            self, text='  Start  ', style='AddressBar.TButton',
            command=self.on_start_btn
        )
        self.begin_btn.pack(side='left', fill='y', padx=5, pady=5)
        # Value in the address bar input field
        self.address = tk.StringVar(
            value=self.settings.default_url.get()
        )
        # Input field can contain url or file path
        self.input_field = ttk.Entry(
            self, style='AddressBar.TEntry',
            textvariable=self.address
        )
        self.input_field.pack(
            side='left', fill='both', expand=True, pady=5
        )
        # Make the <Enter> key trigger the begin btn
        self.input_field.bind(
            '<Return>', lambda e: self.begin_btn.invoke()
        )
        # Progress bar will appear over the input field when needed
        self.progress_bar = ttk.Progressbar(
            orient='horizontal',
            mode='indeterminate',
        )
        # Import from file button
        colour = self.settings.colour_mode.get()
        img_size = (18, 16)
        compound = 'right'
        style='AddressBarImg.TButton'
        self.import_btn = ImageButton(
            self, img_fn=f'import_{colour}.png', img_size=img_size,
            text='Open File', compound=compound,
            command=self.import_file, style=style
        )
        self.import_btn.pack(side='right', padx=5)

    def import_file(self):
        """File button has been clicked"""
        fp, _ = self.master.import_string()
        self.address.set(fp)

    def update_gui_state(self, searching:bool):
        """Enables or disables addressbar widgets"""
        log.debug(f'Updating address bar GUI. Disabled = {searching}')
        state = 'disabled' if searching else 'normal'
        self.begin_btn.config(state=state)
        self.import_btn.config(state=state)
        if searching:
            self.progress_bar.pack(self.input_field.pack_info())
            self.progress_bar.start(10)
            self.input_field.pack_forget()
            return
        self.input_field.pack(self.progress_bar.pack_info())
        self.progress_bar.pack_forget()
        self.progress_bar.stop()

    def on_start_btn(self):
        self.master.nlp(self.address.get())


class CustomTreeView(ttk.Treeview):
    """
        Custom tkinter ttk treeview with a scrollbar and methods for
        handling data.
    """
    # Data displayed in the tree
    data: list[list, list] = []
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
        self.root = self.nametowidget('')
        # Configure treeview
        self.after(10, self._setup_tag_colours)
        self._set_headings(headings, anchor)
        if include_scrollbar:
            self._build_scrollbar()

    def _setup_tag_colours(self):
        return  # disabled
        colour_mode = self.root.notebook.settings_tab.colour_mode.get()
        colours = self.root.style.colours[colour_mode]['background']
        self.tag_configure(ODD, background=colours['tertiary'])
        self.tag_configure(EVEN, background=colours['accent_1'])

    def _build_scrollbar(self):
        """Build scrollbar for treeview"""
        self.scrollbar = ttk.Scrollbar(
            self.master, orient='vertical', command=self.yview,
            style='ArrowLess.Vertical.TScrollbar'
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

    def update_tree(self, data:list[list, list]) -> None:
        """Update the values in this treeview widget"""
        current_data = self.get_children()
        self.data = data  # unfiltered data
        self.filtered_data = self.filter(data)
        # If the data is identical to the previous data, don't bother
        # updating the widget with the new data.
        if self.filtered_data == list(current_data):
            log.debug(
                f'Cancelled update for {self} because the new data ' \
                'is identical to the current data.'
            )
            return  # cancel the rest of the method
        log.debug(f'Updating {self} contents')
        # Replace current data with new data
        self.delete(*current_data)
        i = 0
        for i, row in enumerate(self.filtered_data):
            tag = self.parity(i)
            self.insert('', 'end', values=row, tags=(tag,))
        log.debug(f'Completed update for {self}, item count: {i}')

    def filter(self, data:list[list, list]) -> list[str]:
        """Returns filtered copy of the entered list"""
        # Get list of items to filter out
        hidden = up_list(
            self.hidden_ents.copy() + self.hidden_pos.copy()
        )
        # Create new list without filtered items
        filtered = [
            row for row in data \
            if not any(item in hidden for item in row)
        ]
        log.debug(
            f'Filtered data for {self}, before:[{len(data)}] '  \
            f'after:[{len(filtered)}]'
        )
        return filtered

    def set_filter(
        self, hidden_ents:list, hidden_pos:list, update:bool
    ):
        """Set this treeviews filters"""
        self.hidden_ents = hidden_ents
        self.hidden_pos = hidden_pos
        log.debug(f'Set filters for {self}')
        if update:
            self.update_tree(data=self.data)


class Notebook(ttk.Notebook):
    """Tkinter frame that ouputs results from spacy"""
    def __init__(self, master:tk.Tk):
        log.debug('Initializing notebook')
        super().__init__(master)
        # Create notebook tabs
        self.legend_tab = LegendTab(self)
        self.settings_tab = SettingsTab(self)
        self.results_tab = ResultsTab(self)
        self.contents_tab = ContentTab(self)
        self.help_tab = HelpTab(self)
        # Show notebook tabs
        self.add(self.results_tab, text='Results')
        self.add(self.contents_tab, text='Content')
        self.add(self.legend_tab, text='Legend')
        self.add(self.settings_tab, text='Settings')
        # self.add(self.help_tab, text='Help')


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
    def __init__(self, master):
        log.debug('Initializing results tab')
        super().__init__(master, title='Results')
        self.root = master.master
        colour = master.settings_tab.colour_mode.get()
        # Values for ImageButtons
        img_size=(18, 16)
        compound = 'right'
        style='Compound.TButton'
        # Create export button
        ImageButton(
            self.head, img_fn=f'export_{colour}.png', 
            img_size=img_size, text='Export Results', 
            compound=compound, command=self.root.export_results,
            style=style
        ).pack(side='right', padx=5)
        # Create filter button
        ImageButton(
            self.head, img_fn=f'filter_{colour}.png', 
            img_size=img_size, text='Filter Results', style=style,
            compound=compound, command=self.show_filter_msgbox
        ).pack(side='right', padx=0, pady=5)
        # Create treeview widget
        self.tree = CustomTreeView(
            self, style='Selectable.Treeview', anchor='w',
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

    def update_tree(self, desc:str, data:list[list]):
        """Update treeview with new data"""
        self.head_desc.set(desc)
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
        # export_to_csv(data, fp)


class ContentTab(NotebookTab):
    def __init__(self, master, title='Content', desc=''):
        log.debug('Initializing content tab')
        super().__init__(master, title=title)
        self.content_field = tk.Text(
            self, bd=0, highlightthickness=0, font=('Segoe UI', 9)
        )
        self.content_field = ttk.Label(self, anchor='nw')
        self.content_field.pack(
            fill='both', expand=True, padx=5, pady=5
        )
        self.content_field.bind('<Configure>', self.update_label_wrap)
 
    def update_label_wrap(self, event=None):
        self.content_field.config(wraplength=self.winfo_width() - 10)

    def update_content(self, desc:str, content:str):
        self.head_desc.set(desc)
        self.content_field.config(text=content)


class LegendTab(NotebookTab):
    """Contains widgets explaining spacy lingo stuff"""
    def __init__(self, master, title='Legend', desc=''):
        log.debug('Initializing legend tab')
        super().__init__(master, title=title,)
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


class RadioSetting(SettingWidget):
    """Setting with a radio button"""
    def __init__(
        self, master, label:str, desc:str, var:tk.Variable,
        options:tuple[str], **kw
    ):
        super().__init__(master, label, desc, var, **kw)
        for col, opt in enumerate(options):
            ttk.Radiobutton(
                self, text=opt.title(), value=opt, variable=var,
                style='SettingWidget.TRadiobutton'
            ).grid(column=col, columnspan=1, row=0, sticky='e')


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
        cfg = self.master.master.cfg
        for name, setting in cfg.create_settings_vars():
            setattr(self, name, setting)
        # Values for image buttons
        colour = self.colour_mode.get()
        img_size = (18, 16)
        style='Compound.TButton'
        compound='right'
        root = self.nametowidget('')
        ImageButton(
            self.head, img_fn=f'restart_{colour}.png', 
            img_size=img_size, text='Restart App', compound=compound,
            style=style, command=lambda: root.restart(root)
        ).pack(side='right', padx=5, pady=(5, 6))
        ImageButton(
            self.head, img_fn=f'restore_{colour}.png',
            img_size=img_size, text='Restore Defaults',
            compound=compound, style=style,
            command=lambda: cfg.validate(force_restore=True)
        ).pack(side='right', pady=5)
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
        self.group_entities_checkbox = CheckBoxSetting(
            frame, label='Group Entities',
            desc='Entities of the same type will appear on the same ' \
                 'line',
            var=self.group_entities
        )
        #self.group_entities_checkbox.pack(pack_info)
        self.colour_mode_radio = RadioSetting(
            frame, label='Colour Theme',
            desc='The current colour theme (restart required)',
            var=self.colour_mode, options=('light', 'dark')
        )
        self.colour_mode_radio.pack(pack_info)


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


class CustomMessageBox(tk.Toplevel):
    """A custom popup messagebox"""
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.root = self.nametowidget('')

    def take_controls(self):
        """
            Raises this toplevel above the root and hijacks controls
            from the root
        """
        self.update_idletasks()
        # Configure geometry
        x = self.root.winfo_x() + int(self.root.winfo_width() / 2)
        y = self.root.winfo_y() + int(self.root.winfo_height() / 2)
        x -= int(self.winfo_width() / 2)
        y -= int(self.winfo_height() / 2)
        self.geometry(f'+{x}+{y}')
        # Grab controls
        self.transient(self.root)
        self.grab_set()
        # Pause root until toplevel is destroyed
        self.root.wait_window(self)


class FilterMessageBox(CustomMessageBox):
    def __init__(self):
        super().__init__()
        self.protocol('WM_DELETE_WINDOW', self.on_close)
        colour_mode = self.root.notebook.settings_tab.colour_mode.get()
        colours = self.root.style.colours[colour_mode]
        self.configure(background=colours['background']['primary'])
        # Collect data
        self.results_tab = self.root.notebook.results_tab
        self.entities = self.root.cfg['entities']
        self.pos = self.root.cfg['POS_tags']
        self.hidden_ents = self.results_tab.tree.hidden_ents
        self.hidden_pos = self.results_tab.tree.hidden_pos
        # Create widgets
        notebook = ttk.Notebook(self)
        notebook.pack(fill='both', expand=True, pady=(5, 0))
        self.ents_tab = FilterMessageBoxTab(notebook, title='Entities')
        self.pos_tab = FilterMessageBoxTab(
            notebook, title='Parts Of Speech'
        )
        notebook.add(self.ents_tab, text='Entities') # repeats bad
        notebook.add(self.pos_tab, text='Parts Of Speech')
        # Populate trees
        self.ents_tab.tree.update_tree(
            data=self._sort_data(self.entities, self.hidden_ents)
        )
        self.pos_tab.tree.update_tree(
            data=self._sort_data(self.pos, self.hidden_pos)
        )

    def _get_hidden(self, tab):
        # Extract data
        hidden = [
            tab.tree.item(item)['values'][1] \
            for item in tab.tree.get_children()
        ]
        # Remove spaces from extracted data
        hidden = [i for i in hidden if i != '']
        return hidden

    def on_close(self, apply:bool=False):
        if apply:
            self.hidden_ents = self._get_hidden(self.ents_tab)
            self.hidden_pos = self._get_hidden(self.pos_tab)
            self.results_tab.tree.set_filter(
                self.hidden_ents, self.hidden_pos, update=True
            )
        self.destroy()

    def _sort_data(self, data:list, hidden:list) -> list[list, list]:
        result = []
        hidden = [item.lower() for item in hidden]
        for i in data:
            if i in hidden:
                result.append(['', i.upper()])
                continue
            result.append([i.upper(), ''])
        return result


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
            command=self.move_all_others
        ).pack(side='left', padx=(0, 10), pady=10)
        ttk.Button(
            self, text='Move All', style='Head.TButton',
            command=self.move_all
        ).pack(side='left', padx=(0, 10), pady=10)
        ttk.Button(
            self, text='Apply Filter', style='Head.TButton',
            command=lambda: self.master.master.on_close(apply=True)
        ).pack(side='right', padx=10, pady=10)

    def update_focus(self, item):
        self.tree.focus(item)
        self.tree.selection_set(item)

    def move(self, focus:str):
        values = self.tree.item(focus)['values']
        if not values: return
        values.reverse()
        index = self.tree.index(focus)
        self.tree.delete(focus)
        self.tree.insert(
            '', index, values=values, tags=(self.tree.parity(index),)
        )

    # TODO: clean up repeating code from below.

    def move_selected(self):
        """Move the currently selected item"""
        # Get values for reselecting item
        focus = self.tree.focus()
        index = self.tree.index(focus)
        self.move(focus)
        # Reselect item (because selected item was replaced)
        self.update_focus(self.tree.get_children()[index])

    def move_all(self):
        # Get values for reselecting item
        focus = self.tree.focus()
        index = self.tree.index(focus)
        for item in self.tree.get_children():
            self.move(item)
        # Reselect item (because selected item was replaced)
        self.update_focus(self.tree.get_children()[index])

    def move_all_others(self):
        # Get values for reselecting item
        focus = self.tree.focus()
        index = self.tree.index(focus)
        for item in self.tree.get_children():
            if item == focus: continue
            self.move(item)
        # Reselect item (because selected item was replaced)
        self.update_focus(self.tree.get_children()[index])
