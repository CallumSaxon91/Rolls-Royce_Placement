import os
import sys
import logging
from appdirs import AppDirs

from gui import Root
from utils import validate_dirs
from logs import setup_logs
from constants import APP_NAME


log = logging.getLogger(__name__)

def restart(root):
    root.destroy()
    main()

def main():
    Root(
        name=APP_NAME,
        dirs=directories,
        restart_func=restart
    ).start()

if __name__ == '__main__':
    log.info('Starting application')
    # Validate app directories exist and setup logging
    directories = AppDirs(APP_NAME)
    validate_dirs(directories)
    setup_logs(directories)
    # Create and start GUI
    main()
    # This line will only be read if the GUI has been closed properly
    log.info('Exited application successfully')
