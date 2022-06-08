import logging
from appdirs import AppDirs
from threading import Thread
from spacy import load as get_pipe

from gui import Root
from utils import validate_dirs
from logs import setup_logs
from constants import APP_NAME


log = logging.getLogger(__name__)

def restart(root):
    root.destroy()
    main()

def load_spacy_pipeline(root:Root):
    """Sets new attr as pipeline"""
    pipeline = root.notebook.settings_tab.pipeline.get()
    pipe_suffix = 'sm' if pipeline == 'speed' else 'trf'
    name = f'en_core_web_{pipe_suffix}'

    def load(retries=3):
        if retries <= 0:
            log.error(
                'Exhausted retries for loading spacy pipeline'
            )
            root.addbar.update_gui_state(searching=False)
            return
        log.debug(f'Attempting to load spacy pipeline: {name}')
        try:
            root.pipeline = get_pipe(name)
        except OSError:
            log.error(
                'Failed to load pipeline trying again in 3 seconds'
            )
            root.after(3000, lambda: load(retries-1))
            return
        log.info('Loaded spacy pipeline')
        root.addbar.update_gui_state(searching=False)
    # Disable GUI that requires pipeline to be loaded
    root.addbar.update_gui_state(searching=True)
    # Load pipeline on a separate thread because it can
    # take a while.
    thread = Thread(target=load)
    thread.daemon = True
    thread.start()

def main():
    log.info('Starting application')
    # Validate app directories exist and setup logging
    directories = AppDirs(APP_NAME)
    validate_dirs(directories)
    setup_logs(directories)
    # Create and start GUI
    root = Root(
        name=APP_NAME,
        dirs=directories,
        restart_func=restart
    )
    load_spacy_pipeline(root, )
    root.start()
    # This line will only be read if the GUI has been closed properly
    log.info('Exited application successfully')

if __name__ == '__main__':
    main()
    
