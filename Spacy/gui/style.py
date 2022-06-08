import json
import logging
import tkinter as tk
from tkinter import ttk, font as tkfont

from constants import THEME_PATH
from utils import get_children


log = logging.getLogger(__name__)


class Style(ttk.Style):
    """Custom tkinter style manager"""
    colours: dict
    theme: dict
    
    def __init__(self, root):
        super().__init__(root)
        self.colour_mode = root.notebook.settings_tab.colour_mode.get()
        self.colours = self._load_colour_file('colours.json')
        self.theme = self._load_theme_file('theme.json')
        self._prep_theme()
        self.theme_create(**self.theme)
        self.theme_use('theme')  # name of theme in theme.json

    def _convert_colour(self, value:str):
        try:
            colour_opt, colour_val = value.split('-')
        except ValueError: return value
        except AttributeError: return value
        return self.colours[self.colour_mode][colour_opt][colour_val]

    def _prep_configure(self, widget:str, configure:dict):
        for option, value in configure.items():
            colour = self._convert_colour(value)
            self.theme['settings'][widget]['configure'][option] = colour

    def _prep_map(self, widget:str, map:dict):
        for option, value in map.items():
            for item in value:
                colour = self._convert_colour(item[1])
                self.theme['settings'][widget]['map'][option][value.index(item)][1] = colour

    def _prep_tk_widget(self, widget):
        colours = self.colours[self.colour_mode]
        fg = colours['foreground']
        bg = colours['background']
        # This code is bad. TODO: Rewrite
        if isinstance(widget, tk.Canvas):
            widget.configure(
                background=bg['primary']
            )
        if isinstance(widget, tk.Text):
            widget.configure(
                foreground=fg['primary'], background=bg['primary'],
                font=('Segoe UI', 9), relief='flat', padx=10, pady=10,
                insertbackground=fg['primary']
            )

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
        for widget in get_children(self.master):
            self._prep_tk_widget(widget)

    def _load_colour_file(self, colours_filename:str):
        with open(
            f'{THEME_PATH}/{colours_filename}', 'r'
        ) as colour_file:
            colours = json.load(colour_file)
        return colours

    def _load_theme_file(self, theme_filename:str):
        with open(f'{THEME_PATH}/{theme_filename}', 'r') as theme_file:
            theme = json.load(theme_file)
        return theme
