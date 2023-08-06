"""
yadr
~~~~

The core of the yadn package.
"""
from argparse import ArgumentParser
from importlib.resources import open_text
from pathlib import Path
from typing import Optional

from yadr import maps as m
from yadr.encode import Encoder
from yadr.lex import Lexer
from yadr.model import CompoundResult, Result, TokenInfo
from yadr.parser import dice_map, Parser


# Execute YADN.
def roll(yadn: str,
         yadn_out: bool = False,
         dice_map: Optional[dict[str, dict]] = None
         ) -> str | Result | CompoundResult:
    """Execute a string of YADN to roll dice.

    :param yadn: A string of YADN that defines the die roll to execute.
        YADN is described here: YADN_
    :param yadn_out: (Optional.) Whether the output should be in native
        Python objects or YADN notation. The default is native Python
        objects.
    :return: The result depends on the details of the die roll, but
        could be a :class:int, :class:tuple, or :class:str object.
    :rtype: int or tuple or str

    .. _YADN: https://github.com/pji/yadr/blob/main/docs/dice_notation.rst

    Usage::

        >>> import yadr
        >>>
        >>> yadr.roll('3d6')                        # doctest: +SKIP
        16

    The specific result will depend on the YADN being executed. In the
    example above, it will be an integer in the range of three to
    eighteen that is created by generating three random integers in the
    range of one to six.
    """
    def roll_dice(yadn: str,
                  dice_map: dict,
                  yadn_out: bool) -> str | Result | CompoundResult:
        lexer = Lexer()
        tokens = lexer.lex(yadn)
        parser = Parser()
        parser.dice_map = dice_map
        result: Result | CompoundResult = parser.parse(tokens)
        if yadn_out:
            encoder = Encoder()
            result = encoder.encode(result)
        return result

    if not dice_map:
        dice_map = {}
    default_maps = get_default_maps()
    default_maps.update(dice_map)
    return roll_dice(yadn, default_maps, yadn_out)


# Utility.
def read_file(loc: str | Path) -> str:
    """Read test from a file.

    :param loc: The file system location of the file.
    :return: A :class:str object.
    :rtype: str
    """
    path = Path(loc)
    with open(path) as fh:
        contents = fh.read()
    return contents


def parse_map(yadn: str) -> dict[str, dict]:
    """Parse the contents of a dice mapping file."""
    if ';' in yadn:
        yadn_parts = yadn.split(';')
        dice_map = {}
        for part in yadn_parts:
            assert(';' not in part)
            dice_map.update(parse_map(part))
        return dice_map

    mlexer = m.Lexer()
    mparser = m.Parser()
    tokens = mlexer.lex(yadn)
    name, value = mparser.parse(tokens)
    return {name: value, }


# Command parsing.
def add_dice_map(loc: str) -> dict[str, dict]:
    """Load the dice-maps in the given file into memory.

    :param loc: The location of the file of dice mappings to load.
    :return: None.
    :rtype: NoneType
    """
    yadn = read_file(loc)
    return parse_map(yadn)


def get_default_maps() -> dict[str, dict]:
    """Get the default dice maps."""
    default_file = open_text('yadr.data', 'dice_maps.yadn')
    default_maps_yadn = default_file.read()
    default_file.close()
    return parse_map(default_maps_yadn)


def list_dice_maps() -> str:
    """Get the list of the currently loaded dice maps.

    :return: A :class:str object.
    :rtype: str
    """
    dice_map = get_default_maps()
    maps_ = '\n'.join(dice_map)
    return maps_


def parse_cli() -> None:
    """Parse command line options."""
    # Stand up the parser.
    p = ArgumentParser(
        description='Execute YADN syntax to roll dice.',
        prog='yadr'
    )

    # Define the command line arguments.
    p.add_argument(
        'yadn',
        help='A string of YADN describing the die roll.',
        action='store',
        nargs='?',
        type=str
    )
    p.add_argument(
        '--list_dice_maps', '-l',
        help='List the names of the loaded dice maps.',
        action='store_true'
    )
    p.add_argument(
        '--add_dice_map', '-m',
        help='Load the dice mappings at the given file location.',
        nargs=1,
        action='store',
        type=str
    )

    # Parse and execute the command.
    args = p.parse_args()
    result = ''
    dice_map = {}
    if args.add_dice_map:
        dice_map = add_dice_map(args.add_dice_map[0])
    elif args.list_dice_maps:
        result = list_dice_maps()
    if args.yadn:
        raw_result = roll(args.yadn, True, dice_map)
        result = str(raw_result)
    print(result)
