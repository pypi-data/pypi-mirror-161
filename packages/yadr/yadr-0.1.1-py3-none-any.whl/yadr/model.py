"""
model
~~~~~

Common data elements for the yadr package.
"""
from collections import UserString
from enum import Enum, EnumMeta, auto
from typing import Generic, NamedTuple, Sequence, Union, Tuple, TypeVar


# YADN Tokens.
class Token(Enum):
    START = auto()
    END = auto()
    AS_OPERATOR = auto()
    BOOLEAN = auto()
    CHOICE_OPERATOR = auto()
    CHOICE_OPTIONS = auto()
    COMPARISON_OPERATOR = auto()
    DICE_OPERATOR = auto()
    EX_OPERATOR = auto()
    GROUP_OPEN = auto()
    GROUP_CLOSE = auto()
    KEY = auto()
    KV_DELIMITER = auto()
    MAP = auto()
    MAP_CLOSE = auto()
    MAP_END = auto()
    MAP_OPEN = auto()
    MAPPING_OPERATOR = auto()
    MD_OPERATOR = auto()
    MEMBER = auto()
    MEMBER_DELIMITER = auto()
    NAME = auto()
    NAME_DELIMITER = auto()
    NEGATIVE_SIGN = auto()
    NUMBER = auto()
    OPERATOR = auto()
    OPTIONS_OPERATOR = auto()
    PAIR_DELIMITER = auto()
    POOL = auto()
    POOL_CLOSE = auto()
    POOL_DEGEN_OPERATOR = auto()
    POOL_END = auto()
    POOL_GEN_OPERATOR = auto()
    POOL_OPEN = auto()
    POOL_OPERATOR = auto()
    QUALIFIER = auto()
    QUALIFIER_END = auto()
    QUALIFIER_DELIMITER = auto()
    ROLL_DELIMITER = auto()
    U_POOL_DEGEN_OPERATOR = auto()
    VALUE = auto()
    WHITESPACE = auto()


# Token categories.
op_tokens = (
    Token.CHOICE_OPERATOR,
    Token.COMPARISON_OPERATOR,
    Token.DICE_OPERATOR,
    Token.POOL_GEN_OPERATOR,
    Token.POOL_DEGEN_OPERATOR,
    Token.POOL_OPERATOR,
    Token.U_POOL_DEGEN_OPERATOR,
    Token.OPTIONS_OPERATOR,
    Token.OPERATOR,
    Token.AS_OPERATOR,
    Token.MD_OPERATOR,
    Token.EX_OPERATOR,
    Token.MAPPING_OPERATOR,
)
id_tokens = (
    Token.BOOLEAN,
    Token.NUMBER,
    Token.POOL,
    Token.QUALIFIER,
)

# Symbols for YADN tokens.
# This maps the symbols used in YADN to tokens for lexing. This isn't
# a direct mapping from the YADN specification document. It's just
# the basic things that can be handled by the lexer easily. More
# complicated things are handled through the lexer itself.
yadn_symbols_raw = {
    Token.START: '',
    Token.AS_OPERATOR: '+ -',
    Token.BOOLEAN: 'T F',
    Token.CHOICE_OPERATOR: '?',
    Token.CHOICE_OPTIONS: '',
    Token.COMPARISON_OPERATOR: '< > >= <= != ==',
    Token.DICE_OPERATOR: 'd d! dc dh dl dw',
    Token.EX_OPERATOR: '^',
    Token.GROUP_OPEN: '(',
    Token.GROUP_CLOSE: ')',
    Token.KEY: '',
    Token.KV_DELIMITER: ':',
    Token.MAP: '',
    Token.MAP_CLOSE: '}',
    Token.MAP_END: '',
    Token.MAP_OPEN: '{',
    Token.MAPPING_OPERATOR: 'm',
    Token.MD_OPERATOR: '* / %',
    Token.MEMBER_DELIMITER: ',',
    Token.NEGATIVE_SIGN: '-',
    Token.NAME: '',
    Token.NAME_DELIMITER: '=',
    Token.NUMBER: '0 1 2 3 4 5 6 7 8 9',
    Token.OPTIONS_OPERATOR: ':',
    Token.PAIR_DELIMITER: ',',
    Token.POOL_CLOSE: ']',
    Token.POOL: '',
    Token.POOL_END: '',
    Token.POOL_OPEN: '[',
    Token.POOL_DEGEN_OPERATOR: 'nb ns',
    Token.POOL_GEN_OPERATOR: 'g g!',
    Token.POOL_OPERATOR: 'pa pb pc pf ph pl pr p%',
    Token.QUALIFIER: '',
    Token.QUALIFIER_DELIMITER: '"',
    Token.QUALIFIER_END: '',
    Token.ROLL_DELIMITER: ';',
    Token.U_POOL_DEGEN_OPERATOR: 'C N S',
    Token.VALUE: '',
    Token.WHITESPACE: '',
}


# Classes.
class CompoundResult(Tuple):
    """The result of multiple rolls."""


# Types.
DiceMapping = dict[int, Union[int, str]]
NamedMap = Tuple[str, DiceMapping]
Pool = Tuple[int]
Result = Union[
    int,
    bool,
    str,
    Pool,
    NamedMap,
    None
]
TokenInfo = tuple[Token, Result]


# Symbols by token.
symbols = {k: v.split() for k, v in yadn_symbols_raw.items()}
symbols[Token.WHITESPACE] = [' ', '\t', '\n']
