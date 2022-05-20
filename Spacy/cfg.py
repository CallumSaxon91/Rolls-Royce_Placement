import tkinter as tk
from configparser import ConfigParser
from appdirs import AppDirs
from distutils.util import strtobool
from os import path

from constants import OUTPUT_DIR


defaults = {
    'settings': {
        'auto_save': 'no',
        'auto_save_path': str(OUTPUT_DIR),
        'default_url': 'https://en.wikipedia.org/wiki/'
    },
    'entities': {
        'PEOPLE': 'People, including fictional characters.',
        'NORP': 'Nationalities or religious or political groups.',
        'FAC': 'Buildings, airports, highways, bridges, etc.',
        'ORG': 'Companies, agencies, institutions, etc.',
        'LOC': 'Non-GPE locations, mountain ranges, bodies of water.',
        'PRODUCT': 'Objects, vehicles, foods, etc. (Not services.)',
        'EVENT': 'Named hurricanes, battles, wars, sports events, etc.',
        'WORK_OF_ART': 'Titles of books, songs, etc.',
        'LAW': 'Named documents made into laws.',
        'LANGUAGE': 'Any named language.',
        'DATE': 'Absolute or relative dates or periods.',
        'TIME': 'Times smaller than a day.',
        'PERCENT': 'Percentage',
        'MONEY': 'Monetary values, including unit.',
        'QUANTITY': 'Measurements, as of weight or distance.',
        'ORDINAL': '“first”, “second”, etc.',
        'CARDINAL': 'Numerals that do not fall under another type.'
    },
    'POS_tags': {  # universal part of speech categories
        # open
        'ADJ': 'Adjective',
        'ADV': 'Adverb',
        'INTJ': 'Interjection',
        'NOUN': 'Noun',
        'PROPN': 'Proper Noun',
        'VERB': 'Verb',
        # closed
        'ADP': 'Adposition',
        'AUX': 'Auxiliary',
        'CCONJ': 'Coordinating Conjunction',
        'DET': 'Determiner',
        'NUM': 'Numeral',
        'PART': 'Particle',
        'PRON': 'Pronoun',
        'SCONJ': 'Subordinating Cojunction',
        # other
        'PUNCT': 'Punctuation',
        'SYM': 'Symbol',
        'X': 'Other'
    }
}


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
        for section, options in defaults.items():
            self[section] = options
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
