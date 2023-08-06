"""
operator
~~~~~~~~

Operators for handling the dice part of dice notation.
"""
import random
import operator
from typing import Sequence


# Choice operators.
def choice_options(a: str, b: str) -> tuple[str, str]:
    """Create the options for a choice."""
    return (a, b)


def choice(boolean: bool, options: tuple[str, str]) -> str:
    """Make a choice."""
    result = options[0]
    if not boolean:
        result = options[1]
    return result


# Pool generation operator.
def dice_pool(num: int, size: int) -> tuple[int, ...]:
    """Roll a die pool."""
    return tuple(random.randint(1, size) for _ in range(num))


def exploding_pool(num: int, size: int) -> tuple[int, ...]:
    """Roll a die pool."""
    pool: Sequence[int] = dice_pool(num, size)
    pool = [_explode(n, size) for n in pool]
    return tuple(pool)


# Dice operators.
def concat(num: int, size: int) -> int:
    """Concatenate the least significant digits."""
    base = 10
    pool = dice_pool(num, size)
    pool = pool_modulo(pool, base)
    return pool_concatenate(pool)


def die(num: int, size: int) -> int:
    """Roll a number of same-sized dice and return the result."""
    pool = dice_pool(num, size)
    return sum(pool)


def exploding_die(num: int, size: int) -> int:
    """Roll a number of exploding same-sized dice."""
    return sum(exploding_pool(num, size))


def keep_high_die(num: int, size: int) -> int:
    """Roll a number of dice and keep the highest."""
    pool = dice_pool(num, size)
    return max(pool)


def keep_low_die(num: int, size: int) -> int:
    """Roll a number of dice and keep the lowest."""
    pool = dice_pool(num, size)
    return min(pool)


def wild_die(num: int, size: int) -> int:
    """Roll a number of same-sized dice and return the result."""
    wild = exploding_pool(1, size)
    regular = dice_pool(num - 1, size)
    if wild[0] == 1:
        return 0
    return sum((sum(wild), sum(regular)))


# Pool operators.
def pool_cap(pool: Sequence[int], cap: int) -> tuple[int, ...]:
    """Cap the maximum value in a pool."""
    result = []
    for value in pool:
        if value > cap:
            value = cap
        result.append(value)
    return tuple(result)


def pool_floor(pool: Sequence[int], floor: int) -> tuple[int, ...]:
    """Floor the minimum value in a pool."""
    result = []
    for value in pool:
        if value < floor:
            value = floor
        result.append(value)
    return tuple(result)


def pool_keep_above(pool: Sequence[int], floor: int) -> tuple[int, ...]:
    return tuple(n for n in pool if n >= floor)


def pool_keep_below(pool: Sequence[int], ceiling: int) -> tuple[int, ...]:
    return tuple(n for n in pool if n <= ceiling)


def pool_keep_high(pool: Sequence[int], keep: int) -> tuple[int, ...]:
    """Keep a number of the highest dice."""
    pool = list(pool)
    remove = len(pool) - keep
    for _ in range(remove):
        low_value = max(pool)
        low_index = 0
        for i, n in enumerate(pool):
            if n < low_value:
                low_value = n
                low_index = i
        pool.pop(low_index)
    return tuple(pool)


def pool_keep_low(pool: Sequence[int], keep: int) -> tuple[int, ...]:
    """Keep a number of the lowest dice."""
    pool = list(pool)
    remove = len(pool) - keep
    for _ in range(remove):
        high_value = min(pool)
        high_index = 0
        for i, n in enumerate(pool):
            if n > high_value:
                high_value = n
                high_index = i
        pool.pop(high_index)
    return tuple(pool)


def pool_modulo(pool: Sequence[int], divisor: int) -> tuple[int, ...]:
    """Perform a modulo operation of each member."""
    return tuple(n % divisor for n in pool)


def pool_remove(pool: Sequence[int], cut: int) -> tuple[int, ...]:
    """Remove members of a pool of the given value."""
    return tuple(n for n in pool if n != cut)


# Pool degeneration operators.
def pool_concatenate(pool: Sequence[int]) -> int:
    """Count the dice in the pool."""
    str_value = ''.join((str(m) for m in pool))
    return int(str_value)


def pool_count(pool: Sequence[int]) -> int:
    """Count the dice in the pool."""
    return len(pool)


def pool_sum(pool: Sequence[int]) -> int:
    """Sum the dice in the pool."""
    return sum(pool)


def count_successes(pool: Sequence[int], target: int) -> int:
    """Count the number of successes in the pool."""
    pool = pool_keep_above(pool, target)
    return len(pool)


def count_successes_with_botch(pool: Sequence[int], target: int) -> int:
    botches = len([n for n in pool if n == 1])
    pool = pool_keep_above(pool, target)
    return len(pool) - botches


# Utility functions.
def _seed(seed: int | str | bytes) -> None:
    """Seed the random number generator for testing purposes."""
    if isinstance(seed, str):
        seed = bytes(seed, encoding='utf_8')
    if isinstance(seed, bytes):
        seed = int.from_bytes(seed, 'little')
    random.seed(seed)


def _explode(value: int, size: int) -> int:
    if value == size:
        explode_value = random.randint(1, size)
        value += _explode(explode_value, size)
    return value


# Registration.
ops_by_symbol = {
    # Choice operator.
    '?': choice,

    # Comparison operators.
    '>': operator.gt,
    '<': operator.le,
    '>=': operator.ge,
    '<=': operator.le,
    '==': operator.eq,
    '!=': operator.ne,

    # Dice operators.
    'd': die,
    'd!': exploding_die,
    'dc': concat,
    'dh': keep_high_die,
    'dl': keep_low_die,
    'dw': wild_die,

    # Operators.
    '^': operator.pow,

    # Multiplication/division operators.
    '*': operator.mul,
    '/': operator.floordiv,
    '%': operator.mod,

    # Addition/subtraction operators.
    '+': operator.add,
    '-': operator.sub,

    # Pool degeneration operators.
    'nb': count_successes_with_botch,
    'ns': count_successes,

    # Pool generation operators.
    'g': dice_pool,
    'g!': exploding_pool,

    # Pool operators.
    'pa': pool_keep_above,
    'pb': pool_keep_below,
    'pc': pool_cap,
    'pf': pool_floor,
    'ph': pool_keep_high,
    'pl': pool_keep_low,
    'pr': pool_remove,
    'p%': pool_modulo,

    # Options operator.
    ':': choice_options,

    # Unary pool degeneration operators.
    'C': pool_concatenate,
    'N': pool_count,
    'S': pool_sum,
}
