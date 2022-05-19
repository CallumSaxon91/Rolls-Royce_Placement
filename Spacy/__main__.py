import logging
from appdirs import AppDirs

from gui import AppRoot
from logs import setup_logs
from utils import validate_dirs
from cfg import ConfigManager
from constants import APP_NAME


log = logging.getLogger(__name__)

if __name__ == '__main__':
    # validate directories before starting
    dirs = AppDirs(APP_NAME)
    validate_dirs(dirs)
    # setup logging
    setup_logs(dirs)
    log.debug(f'Starting {APP_NAME}')
    # setup config manager
    cfg = ConfigManager(dirs)
    # start the gui
    app = AppRoot(APP_NAME, dirs, cfg)
    app.mainloop()
