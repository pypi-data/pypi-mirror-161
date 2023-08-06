"""
constants
~~~~~~~~~

Default configuration values for mknames.
"""
from importlib.resources import files
from pathlib import Path

import mkname.data


# Path roots.
data_pkg = files(mkname.data)
data_pkg_str = str(data_pkg)
DATA_ROOT = Path(data_pkg_str)

# File locations.
CONFIG_FILE = DATA_ROOT / 'defaults.cfg'
DEFAULT_CONFIG = DATA_ROOT / 'defaults.cfg'
DEFAULT_DB = DATA_ROOT / 'names.db'
LOCAL_CONFIG = 'mkname.cfg'
LOCAL_DB = 'names.db'

# Word structure.
CONSONANTS = 'bcdfghjklmnpqrstvwxz'
PUNCTUATION = "'-.?!/:@+|•"
SCIFI_LETTERS = 'kqxz'
VOWELS = 'aeiouy'

# Default configuration data.
DEFAULT_CONFIG_DATA = {
    'consonants': CONSONANTS,
    'db_path': str(DEFAULT_DB),
    'punctuation': PUNCTUATION,
    'scifi_letters': SCIFI_LETTERS,
    'vowels': VOWELS,
}
