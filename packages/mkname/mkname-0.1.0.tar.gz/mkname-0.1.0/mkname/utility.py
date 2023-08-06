"""
utility
~~~~~~~

Utility functions for mkname.
"""
from mkname.constants import CONSONANTS, VOWELS
from typing import Sequence

import yadr


# Random number generation.
def roll(yadn: str) -> int:
    """Provide a random number based on the given dice notation."""
    result = yadr.roll(yadn)
    if not isinstance(result, int):
        rtype = type(result).__name__
        msg = ('YADN passed to mkname.utility.roll can only return '
               f'an int. Received type: {rtype}')
        raise ValueError(msg)
    return result


# Word analysis functions.
def calc_cv_pattern(name: str,
                    consonants: Sequence[str] = CONSONANTS,
                    vowels: Sequence[str] = VOWELS) -> str:
    """Determine the pattern of consonants and vowels in the name."""
    name = name.casefold()
    pattern = ''
    for char in name:
        if char in consonants:
            pattern += 'c'
        elif char in vowels:
            pattern += 'v'
        else:
            pattern += 'x'
    return pattern


# Word manipulation functions.
def split_into_syllables(name: str,
                         consonants: Sequence[str] = CONSONANTS,
                         vowels: Sequence[str] = VOWELS) -> tuple[str, ...]:
    """Split a name into syllables. Sort of. It's a simple and very
    inaccurate algorithm.
    """
    pattern = calc_cv_pattern(name, consonants, vowels)
    vowel_indices = [i for i, char in enumerate(pattern) if char == 'v']

    if len(vowel_indices) < 2:
        return (name, )

    else:
        slices = []
        last_location = vowel_indices[0]
        last_split = 0
        for location in vowel_indices[1:]:
            if location - last_location <= 1:
                last_location = location
                continue
            diff = ((location - last_location) // 2) + 1
            split = last_location + diff
            slices.append((last_split, split))
            last_location = location
            last_split = split
        else:
            split = len(name) + 1
            slices.append((last_split, split))

    return tuple(name[s:e] for s, e in slices)
