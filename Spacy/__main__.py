import logging
from appdirs import AppDirs

from gui import AppRoot
from logs import setup_logs
from utils import validate_dirs


log = logging.getLogger(__name__)
APP_NAME = 'SpacyResearch'

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
