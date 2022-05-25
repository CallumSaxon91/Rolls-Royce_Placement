import os
import csv
import logging
from pathlib import Path
from datetime import datetime
from typing import TextIO
from itertools import count
from PIL import Image, ImageTk

from exceptions import NoImageFound
from constants import FILENAME_FORMAT_PREFIX, ASSETS_DIR


log = logging.getLogger(__name__)

def validate_dirs(dirs) -> None:
    """Creates app directories if they don't already exist."""
    log.info('Validating app dirs')
    # create directories in the appdata dir
    Path(dirs.user_config_dir).mkdir(parents=True, exist_ok=True)
    Path(dirs.user_log_dir).mkdir(parents=True, exist_ok=True)
    # create directories with the project files
    for folder_name in ('output', 'assets'):
        Path(
            f'{os.path.dirname(__file__)}\{folder_name}'
        ).mkdir(parents=True, exist_ok=True)

def open_new_file(dir:str, prefix:str='', ext:str='txt') -> TextIO:
    """Create a new file with a unique filename"""
    timestamp = datetime.now().strftime(FILENAME_FORMAT_PREFIX)
    filenames = (
            f'{prefix}_{timestamp}.txt' if i == 0 else \
            f'{prefix}_{timestamp}_{i}.{ext}' for i in count()
        )
    for filename in filenames:
        try:
            path = f'{dir}/{filename}'
            log.debug(f'Creating file at {path}')
            return (Path(path).open('x', encoding='utf-8'))
        except FileExistsError:
            continue
        
def image(filename:str, size:tuple[int, int]) -> ImageTk.PhotoImage:
    """returns PhotoImage object obtained from file path"""
    fp = f'{ASSETS_DIR}\{filename}'
    if not os.path.exists(fp):
        log.error(f'could not find image at fp: {fp}')
        raise NoImageFound
    im = Image.open(fp)
    im = im.resize(size, Image.ANTIALIAS)
    return ImageTk.PhotoImage(im)

def export_to_csv(data:list[list], fp:str):
    """Export 2d array to list"""
    with open(fp, 'w', newline='') as file:
        writer = csv.writer(file, delimiter=',')
        writer.writerows(data)
    log.debug(f'Finished exporting data to csv file at {fp}')

def import_from_csv(fp:str) -> list:
    with open(fp, 'r', newline='') as file:
        rows = csv.read(file, delimiter=',')
    return rows

def low_list(_list:list[str]) -> list[str]:
    """
        Returns a duplicate of the entered list except all contained
        strings are lowercase.
    """
    try:
        new_list = [item.lower() for item in _list.copy()]
        return new_list
    except TypeError:
        # Is this pythonic?
        raise TypeError('Items in list must be of type str')
