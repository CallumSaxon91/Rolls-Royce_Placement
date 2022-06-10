import logging
from configparser import ConfigParser
from appdirs import AppDirs
from os.path import exists
from distutils.util import strtobool
from tkinter import StringVar, BooleanVar

from constants import OUTPUT_PATH


log = logging.getLogger(__name__)


# TODO: this should not be stored here
defaults = {
    'settings': {
        'auto_save': 'no',
        'auto_save_path': str(OUTPUT_PATH),
        'default_url': 'https://en.wikipedia.org/wiki/',
        'group_entities': 'no',
        'colour_mode': 'light',
        'pipeline': 'speed'
    },
    'entities': {
        'PERSON': 'People, including fictional characters.',
        'NORP': 'Nationalities or religious or political groups.',
        'FAC': 'Buildings, airports, highways, bridges, etc.',
        'ORG': 'Companies, agencies, institutions, etc.',
        'GPE': 'Countries, cities, states.',
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
        'CARDINAL': 'Numerals that do not fall under another type.',
        'N/A': 'No entities apply to this word or sentence.'
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
        'SPACE': 'Space',
        'X': 'Other'
    }
}


class ConfigManager(ConfigParser):
    """Custom configuration manager"""
    def __init__(self, dirs:AppDirs):
        log.info('Preparing config manager')
        super().__init__()
        self.dirs = dirs.user_config_dir
        self.fp = f'{self.dirs}/config.ini'
        self.validate()
        self.read(self.fp)
        log.info('Successfully setup config manager')

    def validate(self, force_restore:bool=False):
        """Validate the contents and existance of the config"""
        log.info('Validating config')
        if exists(self.fp) and not force_restore:
            return
        log.info('Restoring configs')
        for section, options in defaults.items():
            self[section] = options
        with open(self.fp, 'w') as file: 
            self.write(file)

    def create_settings_vars(self) -> list:
        """returns list of tk vars created from the configuration"""
        variables = []
        for key, value in self['settings'].items():
            try:
                value = strtobool(value)
                var = BooleanVar
            except ValueError:
                var = StringVar
            var = var(name=key)
            var.set(value)
            variables.append((key, var))
        return variables

    def update(self, section, variable):
        log.info('Updating config file')
        value = variable.get()
        self.set(section, str(variable), str(value))
        with open(self.fp, 'w') as file:
            self.write(file)
        log.debug(
            f'Updated config: <{section}>-<{variable}>-<{value}>'
        )
