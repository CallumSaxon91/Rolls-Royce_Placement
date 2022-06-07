import logging
import tkinter as tk
from tkinter import ttk

from .widgets import ImageButton


log = logging.getLogger(__name__)


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
        self.import_btn.pack(side='right', padx=5, pady=5)

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
