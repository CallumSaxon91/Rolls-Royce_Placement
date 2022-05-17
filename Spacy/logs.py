import logging
from appdirs import AppDirs
from pathlib import Path
from datetime import datetime, timedelta

from utils import open_new_file


FILENAME_FORMAT_PREFIX = '%Y-%m-%d %H-%M-%S'
MAX_LOGFILE_AGE_DAYS = 7

log = logging.getLogger(__name__)

def _destroy_old_logs(dirs:AppDirs):
    for path in Path(dirs.user_log_dir).glob('*.txt'):
        prefix = path.stem.split('_')[0]
        try:
            log_date = datetime.strptime(prefix, FILENAME_FORMAT_PREFIX)
        except ValueError:
            log.warning(f'{path.parent} contains a problematic filename: {path.name}')
            continue
        
        age = datetime.now() - log_date
        if age >= timedelta(days=MAX_LOGFILE_AGE_DAYS):
            log.info(f'removing {path.name} from logs at {path.parent} because the file is older than {MAX_LOGFILE_AGE_DAYS} days')
            path.unlink()

def setup_logs(dirs:AppDirs) -> None:
    file = open_new_file(dirs.user_log_dir)
    handler = logging.StreamHandler(file)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter('[%(asctime)s] %(name)s %(levelname)s: %(message)s'))
    logging.basicConfig(level=logging.DEBUG, handlers=[handler])
    _destroy_old_logs(dirs)