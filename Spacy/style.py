import json
import logging
from tkinter import ttk, font as tkfont

from constants import THEME_DIR


log = logging.getLogger(__name__)


class Style(ttk.Style):
    """Custom tkinter style manager"""
    colours: dict
    theme: dict
    
    def __init__(self, root):
        super().__init__(root)
        self.colours = self._load_colour_file('colours.json')
        self.theme = self._load_theme_file('theme.json')
        self._prep_theme()
        self.theme_create(**self.theme)
        self.theme_use('theme')  # name of theme in theme.json

    def _convert_colour(self, widget:str, section:str, option:str, value:str):
        try:
            colour_opt, colour_val = value.split('-')
        except ValueError: return
        except AttributeError: return
        self.theme['settings'][widget][section][option] = \
        self.colours['light'][colour_opt][colour_val]

    def _prep_configure(self, widget:str, configure:dict):
        for option, value in configure.items():
            self._convert_colour(widget, 'configure', option, value)

    def _prep_map(self, widget:str, map:dict):
        for option, value in map.items():
            pass

    def _prep_theme(self):
        settings = self.theme['settings']
        for widget, w_content in settings.items():
            for section, s_content in w_content.items():
                match section:
                    case "configure":
                        self._prep_configure(widget, s_content)
                    case "map":
                        self._prep_map(widget, s_content)
                    case "layout":
                        # ignore layout sections
                        continue
                    case _:
                        log.warning(
                            'Unknown section in theme file ' \
                            f'{widget}-{section}'
                        )
            
    
    def _load_colour_file(self, colours_filename:str):
        with open(
            f'{THEME_DIR}/{colours_filename}', 'r'
        ) as colour_file:
            colours = json.load(colour_file)
        return colours
    
    def _load_theme_file(self, theme_filename:str):
        with open(f'{THEME_DIR}/{theme_filename}', 'r') as theme_file:
            theme = json.load(theme_file)
        return theme
