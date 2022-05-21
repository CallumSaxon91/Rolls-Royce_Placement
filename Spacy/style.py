import json
import logging
from tkinter import ttk, font as tkfont

from constants import SPACY_DIR


log = logging.getLogger(__name__)


class Style(ttk.Style):
    def __init__(self, root):
        log.debug('Initializing application style')
        super().__init__(root)
        colours = root.cfg['colours']
        with open(f'{SPACY_DIR}\style.json', 'r') as file:
            theme_settings = json.load(file)
        # update the default font
        default_font = tkfont.nametofont('TkDefaultFont')
        default_font.configure(family='Segoe UI',  size=9)
        # apply colours to style
        theme_settings['tk'] = self._apply_colours(
            theme_settings['tk'], colours
        )
        theme_settings['ttk'] = self._apply_colours(
            theme_settings['ttk'], colours
        )
        # create and apply the theme
        self.theme_create(
            themename='default_theme',
            parent='clam',
            settings=theme_settings['ttk']
        )
        self.theme_use('default_theme')
        # get all non-ttk widgets
        widgets = root.winfo_children()
        for widget in widgets:
            if widget.winfo_children():
                widgets.extend(widget.winfo_children())
        # apply style options for non-ttk widgets
        for widget in widgets:
            for widget_name, style in theme_settings['tk'].items():
                if widget.__class__.__name__ == widget_name:
                    widget.config(**style['configure'])
                    
    def _apply_colours(self, theme_settings, colours):
        # This is not complete and needs to be redesigned
        for k1, v1 in theme_settings.items():
            for k2, v2 in v1.items():
                if k2 != 'configure':
                    continue
                for k3, v3 in v2.items():
                    try:
                        theme_settings[k1][k2][k3] = colours[v3]
                    except KeyError:
                        log.error(f'Colour config has no option: {v3}')
                    except AttributeError:
                        log.error(
                            'Colour config does not support ' \
                            f'non-string: {v3}'
                        )
                
        return theme_settings
