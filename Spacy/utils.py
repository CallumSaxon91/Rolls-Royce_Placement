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
    log.info('validating app dirs')
    # directories in the appdata dir
    Path(dirs.user_config_dir).mkdir(parents=True, exist_ok=True)
    Path(dirs.user_log_dir).mkdir(parents=True, exist_ok=True)
    # directories with the project files
    for folder_name in ('output', 'assets'):
        Path(
            f'{os.path.dirname(__file__)}\{folder_name}'
        ).mkdir(parents=True, exist_ok=True)

def open_new_file(dir:str) -> TextIO:
    timestamp = datetime.now().strftime(FILENAME_FORMAT_PREFIX)
    filenames = (f'{timestamp}.txt' if i == 0 else f'{timestamp}_{i}.txt' for i in count())
    for filename in filenames:
        try:
            return (Path(f'{dir}/{filename}').open('x', encoding='utf-8'))
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

def import_from_csv(fp:str) -> list:
    with open(fp, 'r', newline='') as file:
        rows = csv.read(file, delimiter=',')
    return rows
