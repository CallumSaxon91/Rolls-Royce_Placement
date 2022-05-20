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
        self.validate()
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

    def update(self, section, variable):
        self.set(section, str(variable), str(variable.get()))
        with open(self.fp, 'w') as file:
            self.write(file)

    def create_settings_vars(self) -> list:
        """returns list of tk vars created from the configuration"""
        variables = []
        for key, value in self['settings'].items():
            try:
                value = strtobool(value)
                var = tk.BooleanVar(name=key)
            except ValueError:
                var = tk.StringVar(name=key)
            var.set(value)
            variables.append((key, var))
        return variables
