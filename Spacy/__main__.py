import logging
from pathlib import Path
from appdirs import AppDirs

from gui import AppRoot
from logs import setup_logs


log = logging.getLogger(__name__)
APP_NAME = 'SpacyResearch'

def validate_dirs(dirs) -> None:
    """Creates app directories if they don't already exist."""
    log.info('validating app dirs')
    Path(dirs.user_config_dir).mkdir(parents=True, exist_ok=True)
    Path(dirs.user_log_dir).mkdir(parents=True, exist_ok=True)

if __name__ == '__main__':
    # validate directories before starting
    dirs = AppDirs(APP_NAME)
    validate_dirs(dirs)
    # setup logging
    setup_logs(dirs)
    log.debug(f'Starting {APP_NAME}')
    # start the gui
    app = AppRoot(APP_NAME, dirs)
    app.mainloop()
