import logging
import tkinter as tk
from tkinter import ttk

from utils import up_list
from constants import ODD, EVEN


log = logging.getLogger(__name__)


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