"""
constants
~~~~~~~~~

Default configuration values for mknames.
"""
from pathlib import Path


# Path roots.
PKG_ROOT = Path(__file__).parent
DATA_ROOT = PKG_ROOT / 'data'

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
