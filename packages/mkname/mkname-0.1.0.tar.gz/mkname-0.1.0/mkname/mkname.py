"""
mkname
~~~~~~

Tools for building names.
"""
import configparser
from pathlib import Path
from sqlite3 import Connection
from typing import Sequence, Union

from mkname.constants import (
    CONSONANTS,
    DEFAULT_CONFIG,
    DEFAULT_CONFIG_DATA,
    DEFAULT_DB,
    LOCAL_CONFIG,
    LOCAL_DB,
    VOWELS
)
from mkname.mod import compound_names
from mkname.model import Name
from mkname.utility import roll, split_into_syllables


# Initialization functions.
def get_config(location: Union[str, Path] = '') -> dict:
    """Get the configuration.

    :param location: (Optional.) The path to the configuration file.
        If no path is passed, it will default to using the default
        configuration data from mkname.constants.
    :return: A :class:dict object.
    :rtype: dict

    Usage:

        >>> loc = 'tests/data/test_load_config.conf'
        >>> get_config(loc)                 # doctest: +ELLIPSIS
        {'consonants': 'bcd', 'db_path':...'aei'}

    Configuration File Format
    -------------------------
    The file structure of the configuration file is the Windows
    INI-like structure used by Python's configparser module.
    The configuration should be in a 'mkname' section. The following
    keys are possible:

    :param consonants: Characters you define as consonants.
    :param db_path: The path to the names database.
    :param punctuation: Characters you define as punctuation.
    :param scifi_letters: A string of characters you define as being
        characteristic of science fiction names.
    :param vowels: Characters you define as vowels.

    Example::

        [mkname]
        consonants = bcdfghjklmnpqrstvwxz
        db_path = mkname/data/names.db
        punctuation = '-
        scifi_letters: kqxz
        vowels = aeiou
    """
    # Start with the default configuration.
    config_data = DEFAULT_CONFIG_DATA.copy()

    # Convert the passed configuration file location into a Path
    # object so we can check whether it exists. If no location was
    # passed, create a Path for a config file with a default name
    # in the current working directory in case one happens to exist
    # there.
    if location:
        path = Path(location)
    else:
        path = Path(LOCAL_CONFIG)

    # If the given config file doesn't exist, create a new file and
    # add the default config to it. The value of location is checked
    # here to make sure we fall back to default config if we weren't
    # passed a config file location. Otherwise, we'd spew config
    # files into every directory the script is ever run from.
    if location and not path.exists():
        defaults = DEFAULT_CONFIG_DATA.copy()
        content = [f'{key} = {defaults[key]}' for key in defaults]
        content = ['[mkname]', *content]
        with open(path, 'w') as fh:
            fh.write('\n'.join(content))

    # If the given config file now exists, get the config settings
    # from the file and overwrite the default configuration values
    # with the new values from the file.
    if path.is_file():
        config = configparser.ConfigParser()
        config.read(path)
        config_data.update(config['mkname'])

    # If the passed configuration file location was a directory,
    # replacing it would a valid config file could cause unexpected
    # problems. Raise an exception for the user to deal with.
    elif path.is_dir():
        msg = 'Given location is a directory.'
        raise IsADirectoryError(msg)

    return config_data


def init_db(path: Union[str, Path] = '') -> Path:
    """Check if the database exists and initialize it if it doesn't.

    :param path: (Optional.) The path to the names database. It
        defaults to the default name database for the package. If
        nothing exists at that path, it will create a copy of the
        default name database at that location, so you can customize
        the database.
    :return: A :class:pathlib.Path object.
    :rtype: pathlib.Path

    Usage::

        >>> loc = 'mkname/data/names.db'
        >>> init_db(loc)
        PosixPath('mkname/data/names.db')

    Database Structure
    ------------------
    The names database is a sqlite3 database with a table named
    'names'. The names table has the following columns:

    :param id: A unique identifier for the name.
    :param name: The name.
    :param source: The URL where the name was found.
    :param culture: The culture or nation the name is tied to.
    :param date: The approximate year the name is tied to.
    :param kind: A tag for how the name is used, such as a given
        name or a surname.
    """
    # If we aren't passed the location of a database, fall back to the
    # default database for the package.
    if not path:
        path = DEFAULT_DB
    path = Path(path)

    # If there is nothing at the path, copy the default
    # database there.
    if not path.exists():
        with open(DEFAULT_DB, 'rb') as fh:
            contents = fh.read()
        with open(path, 'wb') as fh:
            fh.write(contents)

    # Return the status message.
    return path


# Name making functions.
def build_compound_name(names: Sequence[Name],
                        consonants: Sequence[str] = CONSONANTS,
                        vowels: Sequence[str] = VOWELS) -> str:
    """Construct a new game from two randomly selected names.

    :param names: A list of Name objects to use for constructing
        the new name.
    :param consonants: (Optional.) The characters to consider as
        consonants.
    :param vowels: (Optional.) The characters to consider as vowels.
    :return: A :class:str object.
    :rtype: str

    Usage:

        >>> # Seed the RNG to make this test predictable for this
        >>> # example. Don't do this if you want random names.
        >>> import yadr.operator as yop
        >>> yop.random.seed('spam1')
        >>>
        >>> # The list of names needs to be Name objects.
        >>> names = []
        >>> names.append(Name(1, 'eggs', 'url', '', '', '', 'given'))
        >>> names.append(Name(2, 'spam', 'url', '', '', '', 'given'))
        >>> names.append(Name(3, 'tomato', 'url', '', '', '', 'given'))
        >>>
        >>> # Generate the name.
        >>> build_compound_name(names)
        'Spomato'

    The function takes into account whether the starting letter of
    each name is a vowel or a consonant when determining how to
    create the name. You can affect this by changing which letters
    it treats as consonants or vowels:

        >>> # Seed the RNG to make this test predictable for this
        >>> # example. Don't do this if you want random names.
        >>> import yadr.operator as yop
        >>> yop.random.seed('spam1')
        >>>
        >>> # The list of names needs to be Name objects.
        >>> names = []
        >>> names.append(Name(1, 'eggs', 'url', '', '', '', 'given'))
        >>> names.append(Name(2, 'spam', 'url', '', '', '', 'given'))
        >>> names.append(Name(3, 'tomato', 'url', '', '', '', 'given'))
        >>>
        >>> # Treat 't' as a vowel rather than a consonant.
        >>> consonants = 'bcdfghjklmnpqrsvwxz'
        >>> vowels = 'aeiout'
        >>>
        >>> # Generate the name.
        >>> build_compound_name(names, consonants, vowels)
        'Sptomato'
    """
    root_name = select_name(names)
    mod_name = select_name(names)
    return compound_names(root_name, mod_name, consonants, vowels)


def build_from_syllables(num_syllables: int,
                         names: Sequence[Name],
                         consonants: Sequence[str] = CONSONANTS,
                         vowels: Sequence[str] = VOWELS) -> str:
    """Build a name from the syllables of the given names.

    :param names: A list of Name objects to use for constructing
        the new name.
    :param consonants: (Optional.) The characters to consider as
        consonants.
    :param vowels: (Optional.) The characters to consider as vowels.
    :return: A :class:str object.
    :rtype: str

    Usage:

        >>> # Seed the RNG to make this test predictable for this
        >>> # example. Don't do this if you want random names.
        >>> import yadr.operator as yop
        >>> yop.random.seed('spam1')
        >>>
        >>> # The list of names needs to be Name objects.
        >>> names = []
        >>> names.append(Name(1, 'spameggs', 'url', '', '', '', 'given'))
        >>> names.append(Name(2, 'eggsham', 'url', '', '', '', 'given'))
        >>> names.append(Name(3, 'tomato', 'url', '', '', '', 'given'))
        >>>
        >>> # The number of syllables in the generated name.
        >>> num_syllables = 3
        >>>
        >>> # Generate the name.
        >>> build_from_syllables(num_syllables, names)
        'Shamtomtom'

    The function takes into account whether each letter of each
    name is a vowel or a consonant when determining how to split
    the names into syllables. You can affect this by changing which
    letters it treats as consonants or vowels:

        >>> # Seed the RNG to make this test predictable for this
        >>> # example. Don't do this if you want random names.
        >>> import yadr.operator as yop
        >>> yop.random.seed('spam1')
        >>>
        >>> # The list of names needs to be Name objects.
        >>> names = []
        >>> names.append(Name(1, 'spam', 'url', '', '', '', 'given'))
        >>> names.append(Name(2, 'eggs', 'url', '', '', '', 'given'))
        >>> names.append(Name(3, 'tomato', 'url', '', '', '', 'given'))
        >>>
        >>> # Treat 't' as a vowel rather than a consonant.
        >>> consonants = 'bcdfghjklmnpqrtvwxz'
        >>> vowels = 'aeious'
        >>>
        >>> # Generate the name.
        >>> build_from_syllables(num_syllables, names, consonants, vowels)
        'Gstomtom'
    """
    base_names = [select_name(names) for _ in range(num_syllables)]

    result = ''
    for name in base_names:
        syllables = split_into_syllables(name, consonants, vowels)
        index = roll(f'1d{len(syllables)}') - 1
        syllable = syllables[index]
        result = f'{result}{syllable}'
    return result.title()


def select_name(names: Sequence[Name]) -> str:
    """Select a name from the given list.

    :param names: A list of Name objects to use for constructing
        the new name.
    :return: A :class:str object.
    :rtype: str

    Usage:

        >>> # Seed the RNG to make this test predictable for this
        >>> # example. Don't do this if you want random names.
        >>> import yadr.operator as yop
        >>> yop.random.seed('spam123456')
        >>>
        >>> # The list of names needs to be Name objects.
        >>> names = []
        >>> names.append(Name(1, 'spam', 'url', '', '', '', 'given'))
        >>> names.append(Name(2, 'eggs', 'url', '', '', '', 'given'))
        >>> names.append(Name(3, 'tomato', 'url', '', '', '', 'given'))
        >>>
        >>> # Generate the name.
        >>> select_name(names)
        'eggs'
    """
    index = roll(f'1d{len(names)}') - 1
    return names[index].name
