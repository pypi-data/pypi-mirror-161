"""
db
~~

Functions for handling the database for the names package.
"""
from functools import wraps
from pathlib import Path
import sqlite3
from typing import Any, Callable, Union

from mkname.model import Name


# Connection functions.
def connect_db(location: Union[str, Path]) -> sqlite3.Connection:
    """Connect to the database.
    
    :param location: The path to the database file.
    :return: A :class:sqlite3.Connection object.
    :rtype: sqlite3.Connection
    
    Usage:
    
        >>> loc = 'mkname/data/names.db'
        >>> query = 'select name from names where id = 1;'
        >>> con = connect_db(loc)
        >>> result = con.execute(query)
        >>> tuple(result)
        (('Noah',),)
        >>> disconnect_db(con)
    """
    # Check to make sure the file exists, since sqlite3 fails silently.
    path = Path(location)
    if not path.is_file():
        msg = f'No database at "{path}".'
        raise ValueError(msg)
    
    # Make and return the database connection.
    con = sqlite3.Connection(path)
    return con


def disconnect_db(con: sqlite3.Connection) -> None:
    """Disconnect from the database.
    
    :param con: A database connection.
    :return: None.
    :rtype: :class:NoneType
    
    See connect_db() for usage.
    """
    if con.in_transaction:
        msg = 'Connection has uncommitted changes.'
        raise RuntimeError(msg)
    con.close()


# Connection decorators.
def makes_connection(fn: Callable) -> Callable:
    """A decorator that manages a database connection for the
    decorated function.
    """
    @wraps(fn)
    def wrapper(given_con: Union[sqlite3.Connection, str, Path] = None,
                *args, **kwargs) -> Any:
        if isinstance(given_con, (str, Path)):
            con = connect_db(given_con)
        elif isinstance(given_con, sqlite3.Connection):
            con = given_con
        result = fn(con, *args, **kwargs)
        if isinstance(given_con, (str, Path)):
            disconnect_db(con)
        return result
    return wrapper


# Private query functions.
def _run_query_for_single_column(con: sqlite3.Connection,
                                 query: str) -> tuple[str, ...]:
    """Run the query and return the results."""
    result = con.execute(query)
    return tuple(text[0] for text in result)


# Serialization/deserialization functions.
@makes_connection
def get_names(con: sqlite3.Connection) -> tuple[Name, ...]:
    """Deserialize the names from the database.
    
    :param con: The connection to the database. It defaults to
        creating a new connection to the default database if no
        connection is passed.
    :return: A :class:tuple of :class:Name objects.
    :rtype: tuple
    
    Usage:
    
        >>> # @makes_connection allows you to pass the path of
        >>> # the database file rather than a connection.
        >>> loc = 'tests/data/names.db'
        >>> get_names(loc)                  # doctest: +ELLIPSIS
        (Name(id=1, name='spam', source='eggs', ... kind='given'))
    """
    query = 'select * from names'
    result = con.execute(query)
    return tuple(Name(*args) for args in result)


@makes_connection
def get_names_by_kind(con: sqlite3.Connection, kind: str) -> tuple[Name, ...]:
    """Deserialize the names from the database.
    
    :param con: The connection to the database. It defaults to
        creating a new connection to the default database if no
        connection is passed.
    :param kind: The kind of names to return. By default, this is
        either 'given' or 'surname', but if you have a custom
        database you can add other types.
    :return: A :class:tuple of :class:Name objects.
    :rtype: tuple
    
    Usage:
    
        >>> # @makes_connection allows you to pass the path of
        >>> # the database file rather than a connection.
        >>> loc = 'tests/data/names.db'
        >>> kind = 'given'
        >>> get_names_by_kind(loc, kind)    # doctest: +ELLIPSIS
        (Name(id=1, name='spam', source='eggs', ... kind='given'))
    """
    query = 'select * from names where kind == ?'
    params = (kind, )
    result = con.execute(query, params)
    return tuple(Name(*args) for args in result)


@makes_connection
def get_cultures(con: sqlite3.Connection) -> tuple[str, ...]:
    """Get a list of unique cultures in the database.
    
    :param con: The connection to the database. It defaults to
        creating a new connection to the default database if no
        connection is passed.
    :return: A :class:tuple of :class:Name objects.
    :rtype: tuple
    
    Usage:
    
        >>> # @makes_connection allows you to pass the path of
        >>> # the database file rather than a connection.
        >>> loc = 'tests/data/names.db'
        >>> get_cultures(loc)               # doctest: +ELLIPSIS
        ('bacon', 'pancakes', 'porridge')
    """
    query = 'select distinct culture from names'
    return _run_query_for_single_column(con, query)


@makes_connection
def get_kinds(con: sqlite3.Connection) -> tuple[str, ...]:
    """Get a list of unique kinds in the database.
    
    :param con: The connection to the database. It defaults to
        creating a new connection to the default database if no
        connection is passed.
    :return: A :class:tuple of :class:Name objects.
    :rtype: tuple
    
    Usage:
    
        >>> # @makes_connection allows you to pass the path of
        >>> # the database file rather than a connection.
        >>> loc = 'tests/data/names.db'
        >>> get_kinds(loc)                  # doctest: +ELLIPSIS
        ('given', 'surname')
    """
    query = 'select distinct kind from names'
    return _run_query_for_single_column(con, query)
