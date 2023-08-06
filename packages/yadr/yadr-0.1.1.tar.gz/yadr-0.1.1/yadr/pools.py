"""
pools
~~~~~

A module for handling YADN pools.
"""
from typing import Callable, Sequence

from yadr.base import BaseLexer
from yadr.model import symbols, Token, TokenInfo


class Lexer(BaseLexer):
    def __init__(self) -> None:
        state_map: dict[Token, Callable] = {
            Token.NUMBER: self._number,
            Token.MEMBER_DELIMITER: self._member_delimiter,
            Token.POOL: self._pool,
            Token.POOL_CLOSE: self._pool_close,
            Token.START: self._start,
            Token.WHITESPACE: self._whitespace,
            Token.END: self._start,
        }
        symbol_map: dict[Token, list[str]] = symbols
        bracket_states: dict[Token, Token] = {
            Token.NEGATIVE_SIGN: Token.NUMBER,
            Token.QUALIFIER_DELIMITER: Token.QUALIFIER,
            Token.POOL_OPEN: Token.POOL,
        }
        bracket_ends: dict[Token, Token] = {}
        result_map: dict[Token, Callable] = {
            Token.NUMBER: self._tf_number,
        }
        no_store: list[Token] = [
            Token.POOL_OPEN,
            Token.POOL_CLOSE,
            Token.WHITESPACE,
        ]
        super().__init__(
            state_map,
            symbol_map,
            bracket_states,
            bracket_ends,
            result_map,
            no_store,
            Token.START
        )
        self.process = self._start

    # Value transforms.
    def _tf_number(self, value: str) -> int:
        return int(value)

    # Lexing rules.
    def _member_delimiter(self, char: str) -> None:
        """Lex a member delimiter."""
        can_follow = [
            Token.NUMBER,
            Token.NEGATIVE_SIGN,
            Token.WHITESPACE,
        ]
        self._check_char(char, can_follow)

    def _number(self, char: str) -> None:
        """Lex a member."""
        can_follow = [
            Token.MEMBER_DELIMITER,
            Token.POOL_CLOSE,
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

    def _pool_close(self, char: str) -> None:
        """Lex a pool close."""
        msg = '[ cannot follow a ]'
        raise ValueError(msg)

    def _pool(self, char: str) -> None:
        """Lex a pool open."""
        can_follow = [
            Token.NUMBER,
            Token.NEGATIVE_SIGN,
            Token.WHITESPACE,
        ]
        self._check_char(char, can_follow)

    def _start(self, char: str) -> None:
        """Start lexing the string."""
        can_follow = [
            Token.POOL_OPEN,
        ]
        self._check_char(char, can_follow)


class Parser:
    def parse(self, tokens: Sequence[TokenInfo]) -> tuple[int, ...]:
        """Parse YADN pool tokens."""
        values = []
        for token in tokens:
            kind, value = token
            if kind == Token.NUMBER and isinstance(value, int):
                values.append(value)
            elif kind == Token.NUMBER:
                msg = f'NUMBER tokens should be ints. Found {type(value)}'
                raise TypeError(msg)
        return tuple(values)
