"""
roll
~~~~

Functions that simulate rolling dice using common dice naming syntax.
"""
import random


def seed(seed: int) -> None:
    """Seed the random number generator for testing purposes."""
    if isinstance(seed, str):
        seed = bytes(seed, encoding='utf_8')
    if isinstance(seed, bytes):
        seed = int.from_bytes(seed, 'little')
    random.seed(seed)


def roll(code: str) -> int:
    """Roll dice."""
    # Break down the dice code.
    num_dice_code, dice_and_bonus_code = code.split('d')
    dice_type_code = dice_and_bonus_code
    bonus_code = '0'
    if '+' in dice_and_bonus_code:
        dice_type_code, bonus_code = dice_and_bonus_code.split('+')
    elif '-' in dice_and_bonus_code:
        dice_type_code, bonus_code = dice_and_bonus_code.split('-')
        bonus_code = f'-{bonus_code}'
    num_dice = int(num_dice_code)
    dice_type = int(dice_type_code)
    bonus = int(bonus_code)

    # Roll the dice.
    rolls = tuple(random.randint(1, dice_type) for _ in range(num_dice))
    return sum(rolls) + bonus
