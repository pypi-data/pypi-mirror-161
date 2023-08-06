"""
maps
~~~~

A module for handling YADN dice maps.
"""
from typing import Callable, Optional

from yadr.base import BaseLexer
from yadr.model import NamedMap, Result, symbols, Token, TokenInfo


# Lexing.
class Lexer(BaseLexer):
    def __init__(self) -> None:
        state_map: dict[Token, Callable] = {
            Token.START: self._start,
            Token.END: self._start,
            Token.KV_DELIMITER: self._kv_delimiter,
            Token.MAP_CLOSE: self._map_close,
            Token.MAP_OPEN: self._map_open,
            Token.NAME_DELIMITER: self._name_delimiter,
            Token.NEGATIVE_SIGN: self._negative_sign,
            Token.NUMBER: self._number,
            Token.PAIR_DELIMITER: self._pair_delimiter,
            Token.QUALIFIER: self._qualifier,
            Token.QUALIFIER_END: self._qualifier_end,
            Token.WHITESPACE: self._whitespace,
        }
        symbol_map: dict[Token, list[str]] = symbols
        bracket_states: dict[Token, Token] = {
            Token.NEGATIVE_SIGN: Token.NUMBER,
            Token.QUALIFIER_DELIMITER: Token.QUALIFIER,
        }
        bracket_ends: dict[Token, Token] = {
            Token.QUALIFIER: Token.QUALIFIER_END,
        }
        result_map: dict[Token, Callable] = {
            Token.NUMBER: self._tf_number,
            Token.QUALIFIER: self._tf_qualifier,
        }
        no_store: list[Token] = [
            Token.START,
            Token.QUALIFIER_END,
            Token.WHITESPACE,
        ]
        init_state: Token = Token.START
        super().__init__(
            state_map,
            symbol_map,
            bracket_states,
            bracket_ends,
            result_map,
            no_store,
            init_state
        )

    # Result transformation rules.
    def _tf_number(self, value: str) -> int:
        return int(value)

    def _tf_qualifier(self, value: str) -> str:
        return value[1:-1]

    # Lexing rules.
    def _kv_delimiter(self, char: str) -> None:
        """Lex a key-value delimiter symbol."""
        can_follow = [
            Token.NEGATIVE_SIGN,
            Token.NUMBER,
            Token.QUALIFIER_DELIMITER,
            Token.WHITESPACE,
        ]
        self._check_char(char, can_follow)

    def _map_close(self, char: str) -> None:
        """Lex a map close symbol."""
        can_follow: list[Token] = []
        self._check_char(char, can_follow)

    def _map_open(self, char: str) -> None:
        """Lex a map open symbol."""
        can_follow = [
            Token.MAP_CLOSE,
            Token.QUALIFIER_DELIMITER,
            Token.WHITESPACE,
        ]
        self._check_char(char, can_follow)

    def _name_delimiter(self, char: str) -> None:
        """Lex a name delimiter symbol."""
        can_follow = [
            Token.NEGATIVE_SIGN,
            Token.NUMBER,
            Token.WHITESPACE,
        ]
        self._check_char(char, can_follow)

    def _number(self, char: str) -> None:
        """Processing a number."""
        can_follow = [
            Token.KV_DELIMITER,
            Token.MAP_CLOSE,
            Token.PAIR_DELIMITER,
            Token.WHITESPACE,
        ]

        # Check here if the character is a digit because the checks in
        # Char are currently limited to tokens that no longer than two
        # characters. Check if the state is a number because white
        # space also ends up here, and we want white space to separate
        # numbers.
        if char.isdigit() and self.state == Token.NUMBER:
            self.buffer += char
        else:
            self._check_char(char, can_follow)

    def _negative_sign(self, char: str) -> None:
        """Processing a number."""
        can_follow = [
            Token.NUMBER,
        ]
        self._check_char(char, can_follow)

    def _pair_delimiter(self, char: str) -> None:
        """Lex a pair delimiter symbol."""
        can_follow = [
            Token.NEGATIVE_SIGN,
            Token.NUMBER,
            Token.WHITESPACE,
        ]
        self._check_char(char, can_follow)

    def _qualifier(self, char: str) -> None:
        """Lex a qualifier."""
        self.buffer += char
        if self._is_token_start(Token.QUALIFIER_DELIMITER, char):
            new_state = Token.QUALIFIER_END
            self._change_state(new_state, char)

    def _qualifier_end(self, char: str) -> None:
        can_follow = [
            Token.MAP_CLOSE,
            Token.NAME_DELIMITER,
            Token.PAIR_DELIMITER,
            Token.WHITESPACE,
        ]
        self._check_char(char, can_follow)

    def _start(self, char: str) -> None:
        """Initial lexer state."""
        if self.tokens:
            self.tokens = []
        can_follow = [
            Token.MAP_OPEN,
            Token.WHITESPACE,
        ]
        self._check_char(char, can_follow)


# Parsing.
class Parser:
    def __init__(self):
        self.name = ''
        self.pairs = []
        self.buffer: Optional[int] = None
        self.state = Token.START
        self.state_map = {
            Token.START: self._start,
            Token.END: self._start,
            Token.KEY: self._key,
            Token.NAME: self._name,
            Token.VALUE: self._value,
        }

    def parse(self, tokens: tuple[TokenInfo, ...]) -> NamedMap:
        """Parse YADN dice mapping tokens."""
        for token_info in tokens:
            process = self.state_map[self.state]
            process(token_info)
        return (self.name, {k: v for k, v in self.pairs})

    # Parsing rules.
    def _key(self, token_info: tuple[Token, Result]) -> None:
        token, value = token_info
        if token == Token.NUMBER and isinstance(value, int):
            self.buffer = value
        elif token == Token.KV_DELIMITER:
            self.state = Token.VALUE
        elif token == Token.MAP_CLOSE:
            ...
        else:
            msg = f'KEY cannot contain {token.name}.'
            raise ValueError(msg)

    def _name(self, token_info: tuple[Token, Result]) -> None:
        token, value = token_info
        if token == Token.QUALIFIER:
            self.name = value
        elif token == Token.NAME_DELIMITER:
            self.state = Token.KEY
        elif token == Token.MAP_CLOSE:
            ...
        else:
            msg = f'NAME cannot contain {token.name}.'
            raise ValueError(msg)

    def _value(self, token_info: tuple[Token, Result]) -> None:
        token, value = token_info
        if (token == Token.QUALIFIER
                or token == Token.NUMBER and isinstance(value, int)):
            key = self.buffer
            pair = (key, value)
            self.pairs.append(pair)
            self.buffer = None
        elif token == Token.PAIR_DELIMITER:
            self.state = Token.KEY
        elif token == Token.MAP_CLOSE:
            ...
        else:
            msg = f'VALUE cannot contain {token.name}.'
            raise ValueError(msg)

    def _start(self, token_info: tuple[Token, Result]) -> None:
        token, value = token_info
        if token == Token.MAP_OPEN:
            self.state = Token.NAME
        else:
            msg = f'Dice mapping cannot start with a {value}'
            raise ValueError(msg)
