import logging
import tkinter as tk
from tkinter import ttk

from gui.notebook import NotebookTab
from gui.treeview import CustomTreeView


log = logging.getLogger(__name__)


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