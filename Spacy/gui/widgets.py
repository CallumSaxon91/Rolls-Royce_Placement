import logging
import tkinter as tk
from tkinter import ttk

from utils import image, up_list, parity
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
            tag = parity(i)
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

class ScrollableFrame(ttk.Frame):
    """Tkinter ttk Frame with scrolling capibilities"""
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.canvas = tk.Canvas(
            self, background='gray50', highlightthickness=0
        )
        self.canvas.pack(side='left', fill='both', expand=True)
        self.canvas.bind(
            '<Configure>', self._on_canvas_resize, add=True
        )
        self.scrollbar = ttk.Scrollbar(self, command=self.canvas.yview)
        self.scrollbar.pack(side='right', fill='y')
        self.frame = ttk.Frame(self.canvas, style='TFrame')
        self.canvas.create_window(
            (0, 0), anchor='nw',
            window=self.frame
        )
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.frame.bind(
            '<Configure>',
            lambda: self.canvas.config(
                scrollregion=self.canvas.bbox("all")
            )
        )
        for i in range(50):
            ttk.Label(self.frame, text="Sample scrolling label").pack()
        self._on_canvas_resize()

    def _on_canvas_resize(self, event=None):
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        self.frame.config(width=w)
        if self.frame.winfo_width() < h:
            self.frame.config(height=h)
        print(w, h)
