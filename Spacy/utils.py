import logging
from pathlib import Path
from datetime import datetime
from typing import TextIO
from itertools import count


FILENAME_FORMAT_PREFIX = '%Y-%m-%d %H-%M-%S'

log = logging.getLogger(__name__)

def validate_dirs(dirs) -> None:
    """Creates app directories if they don't already exist."""
    log.info('validating app dirs')
    Path(dirs.user_config_dir).mkdir(parents=True, exist_ok=True)
    Path(dirs.user_log_dir).mkdir(parents=True, exist_ok=True)
    Path(
        __file__.removesuffix(f'{__name__}.py') + 'output'
    ).mkdir(parents=True, exist_ok=True)

def open_new_file(dir:str) -> TextIO:
    timestamp = datetime.now().strftime(FILENAME_FORMAT_PREFIX)
    filenames = (f'{timestamp}.txt' if i == 0 else f'{timestamp}_{i}.txt' for i in count())
    for filename in filenames:
        try:
            return (Path(f'"{dir}/{filename}"').open('x', encoding='utf-8'))
        except FileExistsError:
            continue
