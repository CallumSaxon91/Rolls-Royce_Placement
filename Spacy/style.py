from tkinter import ttk


theme_settings = {
    "tk": {
        "Text": {
            "configure": {
                "borderwidth": 1,
                "relief": "groove"
            }
        }
    },
    "ttk": {
        "TFrame": {
            "configure": {
            }
        },
        "AddressBar.TFrame": {
            "configure": {
            }
        },
        "AddressBar.TButton": {
            "configure": {
                "background": "gray85",
                "focuscolor": "gray85",
                "borderwidth": 2,
                "relief": "groove",
                "padding": [10, 0, 10, 0]
            },
            "map": {
                "relief": [
                    ["pressed", "sunken"],
                ],
                "background": [
                    ["pressed", "gray80"]
                ],
                "focuscolor": [
                    ["pressed", "gray80"]
                ]
            }
        },
        "AddressBar.TEntry": {
            "configure": {
                "padding": [3, 0, 3, 0],
                "selectforeground": "white",
                "selectbackground": "DodgerBlue"
            }
        },
        "TNotebook.Tab": {
            "configure": {
                "background": "gray75",
                "focuscolor": "gray85",
                "padding": [5, 0, 5, 0]
            },
            "map": {
                "background": [
                    ["selected", "gray85"]
                ]
            }
        }
    }
}


class Style(ttk.Style):
    def __init__(self, root):
        super().__init__(root)

        self.theme_create(
            themename='default_theme',
            parent='clam',
            settings=theme_settings['ttk']
        )
        self.theme_use('default_theme')

        widgets = root.winfo_children()
        for widget in widgets:
            if widget.winfo_children():
                widgets.extend(widget.winfo_children())

        # apply style options for non-ttk widgets
        for widget in widgets:
            for widget_name, style in theme_settings['tk'].items():
                if widget.__class__.__name__ == widget_name:
                    widget.config(**style['configure'])
