import logging
from appdirs import AppDirs
from pathlib import Path

from gui import AppRoot
from logs import setup_logs


log = logging.getLogger(__name__)

def validate_dirs(dirs) -> None:
    """Creates app directories if they don't already exist."""
    log.info('validating app dirs')
    Path(dirs.user_config_dir).mkdir(parents=True, exist_ok=True)
    Path(dirs.user_log_dir).mkdir(parents=True, exist_ok=True)

if __name__ == '__main__':
    app_name = 'SpacyResearch'

    # validate directories before starting
    dirs = AppDirs(app_name)
    validate_dirs(dirs)

    # setup logging
    setup_logs(dirs)
    log.debug(f'Starting {app_name}')

    # start the gui
    app = AppRoot(app_name, dirs)
    app.mainloop()


# import spacy

# nlp = spacy.load('en_core_web_sm')

# text = ''

# doc = nlp(text)
