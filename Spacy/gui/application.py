import logging
import csv
import tkinter as tk
from tkinter import filedialog
from appdirs import AppDirs
from spacy import load as get_pipe
from threading import Thread

from .widgets import Notebook, AddressBar
from .style import Style
from config import ConfigManager
from constants import ASSETS_PATH


log = logging.getLogger(__name__)


class Root(tk.Tk):
    """Root of the GUI application"""
    def __init__(self, name:str, dirs:AppDirs, config:ConfigManager):
        super().__init__()
        self.dirs = dirs
        self.cfg = config(dirs)
        # Configure root window
        self.title(name)
        self.geometry('700x400')
        self.iconbitmap(f'{ASSETS_PATH}/icon.ico')
        # Create and show controls
        self.notebook = Notebook(self)
        self.addbar = AddressBar(self)
        self.addbar.pack(fill='x')
        self.notebook.pack(fill='both', expand=True)
        # Initialize style
        self.style = Style(self)

    def start(self):
        """Start the GUI application"""
        self.load_spacy_pipeline(name='en_core_web_sm')
        self.mainloop()

    def load_spacy_pipeline(self, name):
        """Sets new attr to Root as pipeline"""
        log.debug('Loading spacy pipeline')
        def load():
            self.pipeline = get_pipe(name)
            log.info('Loaded spacy pipeline')
        # Load pipeline on a separate thread because it can
        # take a while.
        thread = Thread(target=load)
        thread.daemon = True
        thread.start()

    def import_string(self) -> tuple[str, str]:
        """Import a string from a text file and return it"""
        log.debug('Importing string from text file')
        # Open existing file to read from
        file = filedialog.askopenfile(
            defaultextension='.txt',
            filetypes=(('Text File', '*.txt'),)
        )
        # Return if no file is selected
        if not file: return
        data = file.read()
        file.close()
        log.debug('Successfully import string from text file')
        return file.name, data

    def export_results(self):
        """Export results from results tab to file"""
        log.debug('Exporting results to output file')
        # Create and open the output file
        file = filedialog.asksaveasfile(
            initialfile='output.csv',
            defaultextension='.csv',
            filetypes=(('CSV File', '*.csv'),)
        )
        # Return if no output file has been selected
        if not file: return
        # Collect data from results treeview
        tree = self.notebook.results_tab.tree
        tree_data = [
            tree.item(row)['values'] \
            for row in tree.get_children()
        ]
        # Write data to output file
        writer = csv.writer(file)
        writer.writerows(tree_data)
        file.close()
        log.info(f'Exported {len(tree_data)} rows to {file}')
