"""
parse
~~~~~

Parse dice notation.
"""
from functools import wraps
import operator
from typing import Callable, Generic, Optional, Sequence, TypeVar

from yadr import operator as yo
from yadr.model import (
    CompoundResult,
    Result,
    Token,
    TokenInfo,
    op_tokens,
    id_tokens
)


# The dice map.
# This needs to not be a global value, but it will require a very large
# change to this module to get that to work. This will work for now.
dice_map: dict[str, dict] = {}


# Parser specific operations.
def map_result(result: int | tuple[int, ...],
               key: str) -> str | tuple[str, ...]:
    """Map a roll result to a dice map."""
    if isinstance(result, int):
        return dice_map[key][result]
    new_result = [map_result(n, key) for n in result]
    str_result = tuple(str(item) for item in new_result)
    return str_result


# Utility classes and functions.
class Tree:
    """A binary tree."""
    def __init__(self,
                 kind: Token,
                 value: Result,
                 left: Optional['Tree'] = None,
                 right: Optional['Tree'] = None,
                 dice_map: Optional[dict[str, dict]] = None) -> None:
        self.kind = kind
        self.value = value
        self.left = left
        self.right = right
        if dice_map is None:
            dice_map = {}
        self.dice_map = dice_map

    def __repr__(self):
        name = self.__class__.__name__
        return f'{name}(kind={self.kind}, value={self.value})'

    def compute(self):
        if self.kind in id_tokens:
            return self.value
        left = self.left.compute()
        right = self.right.compute()
        if self.kind in op_tokens:
            ops_by_symbol = yo.ops_by_symbol
            ops_by_symbol['m'] = self._map_result
            op = ops_by_symbol[self.value]
        else:
            msg = f'Unknown token {self.kind}'
            raise TypeError(msg)
        return op(left, right)

    def _map_result(self, result: int | tuple[int, ...],
                    key: str) -> str | tuple[str, ...]:
        """Map a roll result to a dice map."""
        if isinstance(result, int):
            return self.dice_map[key][result]
        new_result = [self._map_result(n, key) for n in result]
        str_result = tuple(str(item) for item in new_result)
        return str_result


class Unary(Tree):
    """A unary tree."""
    def __init__(self,
                 kind: Token,
                 value: Result,
                 child: Optional['Tree'] = None) -> None:
        self.kind = kind
        self.value = value
        self.child = child

    def compute(self):
        if self.kind in id_tokens:
            return self.value
        child = self.child.compute()
        if self.kind in op_tokens:
            op = yo.ops_by_symbol[self.value]
        return op(child)


# Parser class.
class Parser:
    def __init__(self) -> None:
        self.dice_map: dict[str, dict] = dict()
        self.top_rule = self._map_operator

    # Public method.
    def parse(self, tokens: Sequence[TokenInfo]) -> Result | CompoundResult:
        if (Token.ROLL_DELIMITER, ';') not in tokens:
            return self._parse_roll(tokens)        # type: ignore

        rolls = []
        while (Token.ROLL_DELIMITER, ';') in tokens:
            index = tokens.index((Token.ROLL_DELIMITER, ';'))
            roll = tokens[0:index]
            rolls.append(roll)
            tokens = tokens[index + 1:]
        else:
            rolls.append(tokens)
        results: Sequence[Result] = []
        for roll in rolls:
            results.append(self.parse(roll))       # type: ignore
            results = [result for result in results if result is not None]
        if len(results) > 1:
            return CompoundResult(results)
        elif results:
            return results[0]
        return None

    def _parse_roll(self, tokens: Sequence[TokenInfo]) -> Result:
        """Parse a sequence of YADN tokens."""
        def make_tree(kind, value):
            return Tree(kind, value, dice_map=self.dice_map)

        trees = [make_tree(kind, value) for kind, value in tokens]
        trees = trees[::-1]
        parsed = self.top_rule(trees)
        if parsed:
            return parsed.compute()
        return None

    # Parsing rules.
    def _identity(self, trees: list[Tree]) -> Tree | None:
        """Parse an identity."""
        identity_tokens = [
            Token.BOOLEAN,
            Token.NUMBER,
            Token.POOL,
            Token.QUALIFIER,
        ]
        tree = trees.pop()
        if tree.kind in identity_tokens:
            return tree
        elif tree.kind == Token.MAP:
            name, map_ = tree.value                          # type: ignore
            self.dice_map[name] = map_
            return None
        elif tree.kind == Token.GROUP_OPEN:
            expression = self.top_rule(trees)
            if trees[-1].kind == Token.GROUP_CLOSE:
                _ = trees.pop()
            return expression
        else:
            msg = f'Unrecognized token {tree.kind}'
            raise TypeError(msg)

    def _pool_gen_operator(self, trees: list[Tree]) -> Tree:
        """Parse pool generation operator."""
        rule = self._binary_operator
        rule_affects = Token.POOL_GEN_OPERATOR
        next_rule = self._identity
        return rule(rule_affects, next_rule, trees)

    def _pool_operator(self, trees: list[Tree]) -> Tree:
        """Parse pool operator."""
        rule = self._binary_operator
        rule_affects = Token.POOL_OPERATOR
        next_rule = self._pool_gen_operator
        return rule(rule_affects, next_rule, trees)

    def _u_pool_degen_operator(self, trees: list[Tree]) -> Tree:
        """Parse unary pool degeneration."""
        rule = self._unary_operator
        rule_affects = Token.U_POOL_DEGEN_OPERATOR
        next_rule = self._pool_operator
        return rule(rule_affects, next_rule, trees)

    def _pool_degen_operator(self, trees: list[Tree]) -> Tree:
        """Parse unary pool degeneration."""
        rule = self._binary_operator
        rule_affects = Token.POOL_DEGEN_OPERATOR
        next_rule = self._u_pool_degen_operator
        return rule(rule_affects, next_rule, trees)

    def _dice_operator(self, trees: list[Tree]) -> Tree:
        """Parse dice operators."""
        rule = self._binary_operator
        rule_affects = Token.DICE_OPERATOR
        next_rule = self._pool_degen_operator
        return rule(rule_affects, next_rule, trees)

    def _ex_operator(self, trees: list[Tree]) -> Tree:
        """Parse exponentiation."""
        rule = self._binary_operator
        rule_affects = Token.EX_OPERATOR
        next_rule = self._dice_operator
        return rule(rule_affects, next_rule, trees)

    def _md_operator(self, trees: list[Tree]) -> Tree:
        """Parse addition and subtraction."""
        rule = self._binary_operator
        rule_affects = Token.MD_OPERATOR
        next_rule = self._ex_operator
        return rule(rule_affects, next_rule, trees)

    def _as_operator(self, trees: list[Tree]) -> Tree:
        """Parse addition and subtraction."""
        rule = self._binary_operator
        rule_affects = Token.AS_OPERATOR
        next_rule = self._md_operator
        return rule(rule_affects, next_rule, trees)

    def _comparison_operator(self, trees: list[Tree]) -> Tree:
        """Parse comparisons."""
        rule = self._binary_operator
        rule_affects = Token.COMPARISON_OPERATOR
        next_rule = self._as_operator
        return rule(rule_affects, next_rule, trees)

    def _options_operator(self, trees: list[Tree]) -> Tree:
        """Parse comparisons."""
        rule = self._binary_operator
        rule_affects = Token.OPTIONS_OPERATOR
        next_rule = self._comparison_operator
        return rule(rule_affects, next_rule, trees)

    def _choice_operator(self, trees: list[Tree]) -> Tree:
        """Parse chocies."""
        rule = self._binary_operator
        rule_affects = Token.CHOICE_OPERATOR
        next_rule = self._options_operator
        return rule(rule_affects, next_rule, trees)

    def _map_operator(self, trees: list[Tree]) -> Tree:
        """Parse dice mapping operators."""
        rule = self._binary_operator
        rule_affects = Token.MAPPING_OPERATOR
        next_rule = self._choice_operator
        return rule(rule_affects, next_rule, trees)

    # Base rules.
    def _binary_operator(self, rule_affects: Token,
                         next_rule: Callable,
                         trees: list[Tree]) -> Tree:
        """Parse a binary operator."""
        left = next_rule(trees)
        while trees and trees[-1].kind == rule_affects:
            tree = trees.pop()
            tree.left = left
            tree.right = next_rule(trees)
            left = tree
        return left

    def _unary_operator(self, rule_affects: Token,
                        next_rule: Callable,
                        trees: list[Tree]) -> Tree:
        """Parse an unary operator."""
        if trees[-1].kind == rule_affects:
            tree = trees.pop()
            unary = Unary(tree.kind, tree.value)
            unary.child = next_rule(trees)
            return unary
        return next_rule(trees)
