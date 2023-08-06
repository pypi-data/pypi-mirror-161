"""
model
~~~~~

The data model for the mkname package.
"""
from typing import NamedTuple


class Name(NamedTuple):
    """A name to use for generation.
    
    :param id: A unique identifier for the name.
    :param name: The name.
    :param source: The URL where the name was found.
    :param culture: The culture or nation the name is tied to.
    :param date: The approximate year the name is tied to.
    :param kind: A tag for how the name is used, such as a given
        name or a surname.
    """
    id: int
    name: str
    source: str
    culture: str
    date: int
    gender: str
    kind: str
