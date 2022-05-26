from os import path


# Directories
SPACY_DIR = path.dirname(__file__)
ASSETS_DIR = SPACY_DIR + r'\assets'
OUTPUT_DIR = SPACY_DIR + r'\output'
THEME_DIR = SPACY_DIR + r'\theme'
# Tkinter treeview row tags
ODD = 'odd'
EVEN = 'even'
# Other
FILENAME_FORMAT_PREFIX = '%Y-%m-%d %H-%M-%S'
MAX_LOGFILE_AGE_DAYS = 7
APP_NAME = 'SpacyResearch'
