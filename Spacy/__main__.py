import logging
from appdirs import AppDirs

from gui import Root
from utils import validate_dirs
from logs import setup_logs
from config import ConfigManager
from constants import APP_NAME


log = logging.getLogger(__name__)

if __name__ == '__main__':
    # Validate app directories exist and setup logging
    directories = AppDirs(APP_NAME)
    validate_dirs(directories)
    setup_logs(directories)
    # GUI main loop
    Root(
        name=APP_NAME,
        dirs=directories,
        config=ConfigManager
    ).start()
    # This line will only be read if the GUI has been closed properly
    log.info('Exited application successfully')
