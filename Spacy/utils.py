import os
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
            fp = f'{dir}/{filename}'
            if not os.path.exists(fp):
                break
            return (Path(f'{dir}/{filename}').open('x', encoding='utf-8'))
        except FileExistsError:
            continue

        
def image(filename:str, size:tuple[int, int]) -> ImageTk.PhotoImage:
    """returns PhotoImage object obtained from file path"""
    fp = ASSETS_DIR + f'\{filename}'
    print(fp)
    if not os.path.exists(fp):
        log.error(f'could not find image at fp: {fp}')
        raise NoImageFound
    im = Image.open(fp)
    im = im.resize(size, Image.ANTIALIAS)
    return ImageTk.PhotoImage(im)
<<<<<<< Updated upstream
=======

def up_list(_list:list[str]) -> list[str]:
    """
        Returns a duplicate of the entered list except all contained
        strings are uppercase.
    """
    try:
        new_list = [item.upper() for item in _list.copy()]
        return new_list
    except TypeError:
        # Is this pythonic?
        raise TypeError('Items in list must be of type str')

def web_scrape(
        url:str, search_for:str='p', remove_linebreak:bool=False
    ) -> dict:
    """Returns scraped web content"""
    result = requests.get(url)
    soup = BeautifulSoup(result.content, 'html.parser')
    content = [item.get_text() for item in soup.find_all(search_for)]
    if remove_linebreak:
        content = [item.replace('\n', '') for item in content]
    title = soup.title.string
    return title, content

def parse_string_content(pipeline:Language, string:str) -> list[list]:
    """Returns parsed string content as [word, entity, pos]"""
    document = pipeline(string)
    parsed = np.array(
        [[token.text, token.ent_type_, token.pos_] \
        for token in document]
    )
    # Replace empty strings with 'N/A' in the entitiy
    # column.
    try:
        parsed[np.where(parsed=='')] = 'N/A'
    except ValueError:
        pass
    return parsed.tolist()

def parity(integer:int) -> str:
    """Returns 'even' or 'odd' when given an integer"""
    return EVEN if integer % 2 == 0 else ODD

def get_children(widget) -> list:
    children = widget.winfo_children()
    for child in children:
        inner_children = child.winfo_children()
        if inner_children:
            children.extend(inner_children)
    return children

#
>>>>>>> Stashed changes
