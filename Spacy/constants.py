from os import path

SPACY_DIR = path.dirname(__file__)
ASSETS_DIR = SPACY_DIR + r'\assets'
OUTPUT_DIR = SPACY_DIR + r'\output'
FILENAME_FORMAT_PREFIX = '%Y-%m-%d %H-%M-%S'
MAX_LOGFILE_AGE_DAYS = 7
APP_NAME = 'SpacyResearch'
# for tkinter treeview
ODD = 'odd'
EVEN = 'even'