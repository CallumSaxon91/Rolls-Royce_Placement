import logging
import tkinter as tk
from tkinter import ttk

from .widgets import (
    ImageButton, CustomTreeView, CustomMessageBox,
    RadioSetting, TextSetting, CheckBoxSetting,
    ScrollableFrame
)
from utils import parity


log = logging.getLogger(__name__)


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
        self.test_tab = TestTab(self)
        # Show notebook tabs
        self.add(self.results_tab, text='Results')
        self.add(self.contents_tab, text='Content')
        self.add(self.legend_tab, text='Legend')
        self.add(self.settings_tab, text='Settings')
        self.add(self.test_tab, text='Testing')
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
        ).pack(side='right', padx=5, pady=5)
        # Create filter button
        ImageButton(
            self.head, img_fn=f'filter_{colour}.png', 
            img_size=img_size, text='Filter Results', style=style,
            compound=compound, command=self.show_filter_msgbox
        ).pack(side='right', pady=5)
        # Create treeview widget
        self.tree = CustomTreeView(
            self, style='Selectable.Treeview', anchor='w',
            headings=('words', 'entity type', 'part of speech')
        )
        self.tree.pack(
            side='left', fill='both', expand=True
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
        if desc:
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
        super().__init__(master, title=title, desc=desc)
        self.content_field = ttk.Label(self, anchor='nw')
        self.content_field.pack(
            fill='both', expand=True, padx=5, pady=5
        )
        self.content_field.bind('<Configure>', self.update_label_wrap)
 
    def update_label_wrap(self, event=None):
        self.content_field.config(wraplength=self.winfo_width() - 10)

    def update_content(self, desc:str, content:str):
        if desc:
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
        self.tree.pack(side='left', fill='both', expand=True)
        # populate tree
        settings = master.master.cfg
        entities = settings['entities']
        word_classes = settings['POS_tags']
        for i, (entity, pos) in enumerate(
            zip(entities.items(), word_classes.items())
        ):
            tag = parity(i)
            values = entity + pos
            values = [
                v.upper() if values.index(v) % 2 == 0 else v \
                for v in values
            ]
            self.tree.insert('', 'end', values=values, tags=(tag,))


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
        scrollframe = ScrollableFrame(self)
        scrollframe.pack(fill='both', expand=True)
        frame = scrollframe.frame
        pack_info = {
            'fill': 'x', 'side': 'top', 'anchor': 'w',
            'padx': 10, 'pady': 10
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
        self.group_entities_checkbox.pack(pack_info)
        self.colour_mode_radio = RadioSetting(
            frame, label='Colour Theme',
            desc='The current colour theme (restart required)',
            var=self.colour_mode, options=('light', 'dark')
        )
        self.colour_mode_radio.pack(pack_info)
        self.pipeline_radio = RadioSetting(
            frame, label='NLP Pipeline',
            desc='Preference for NLP Pipeline (restart required)',
            options=('speed', 'accuracy'),
            var=self.pipeline,
        )
        self.pipeline_radio.pack(pack_info)


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


class TestTab(NotebookTab):
    """Tab containing helpful info on how to use the app"""
    def __init__(self, master):
        log.debug('Initializing test tab')
        super().__init__(master, title='Test')
        scrollframe = ScrollableFrame(self)
        scrollframe.pack(fill='both', expand=True)


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
            '', index, values=values, tags=(parity(index),)
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
