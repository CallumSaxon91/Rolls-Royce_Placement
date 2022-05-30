import logging
from appdirs import AppDirs

from gui import Root
from utils import validate_dirs
from logs import setup_logs
from config import ConfigManager
from constants import APP_NAME


log = logging.getLogger(__name__)

if __name__ == '__main__':
    directories = AppDirs(APP_NAME)
    validate_dirs(directories)
    setup_logs(directories)
    Root(
        name=APP_NAME,
        dirs=directories,
        config=ConfigManager
    ).start()
