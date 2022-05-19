import tkinter as tk
from configparser import ConfigParser
from appdirs import AppDirs
from distutils.util import strtobool
from os import path

from constants import OUTPUT_DIR


class ConfigManager(ConfigParser):
    """Configuration manager for spacy research project"""
    def __init__(self, dirs:AppDirs):
        super().__init__()
        self.dirs = dirs.user_config_dir
        self.fp = f'{self.dirs}/config.ini'
        self.validate(force_restore=True)
        self.read(self.fp)

    def validate(self, force_restore:bool=False):
        """create config file if it doesnt exist"""
        if path.exists(self.fp) and not force_restore:
            return
        self['settings'] = {
            'auto_save': 'no',
            'auto_save_path': OUTPUT_DIR,
            'quick_search': 'yes'
        }
        with open(self.fp, 'w') as file: 
            self.write(file)

    def update(self, section, option, value):
        return  # TODO: here
        self.set(section, option, str(value.get()))
        with open(self.fp, 'w') as file:
            print('wrote', self.sections('settings'))
            self.write(file)

    def create_settings_vars(self) -> list:
        """returns list of tk vars created from the configuration"""
        variables = []
        for k, val in self['settings'].items():
            try:
                val = strtobool(val)
                var = tk.BooleanVar()
            except ValueError:
                var = tk.StringVar()
            var.set(val)
            var.trace_add(
                'write', 
                lambda *_: self.update('settings', k, var)
            )
            variables.append((k, var))
        return variables
