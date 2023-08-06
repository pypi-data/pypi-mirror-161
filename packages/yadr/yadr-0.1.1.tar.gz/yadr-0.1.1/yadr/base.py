"""
base
~~~~

Base classes for the yadr package.
"""
from abc import ABC, abstractmethod
from typing import Callable, Optional

from yadr.model import CompoundResult, Result, Token, TokenInfo


# Utility functions.
def _mutable(value, type_=list):
    """Return an empty mutable type to avoid bugs where you put a
    mutable in the signature.
    """
    if not value:
        value = type_()
    return value


# Base classes.
class BaseLexer(ABC):
    """An abstract base class for building lexers.

    :class:BaseLexer lexers are state machines used for translating
    a text string into tokens for parsing. It accomplishes this by
    processing the string one character at a time, allowing the
    current state of the lexer to determine whether the character is
    legal and what should be done with it.


    State
    -----
    The current state of the lexer is determined by the value of
    the `state` attribute of the lexer. Its value will be a member
    of the enumeration used to define the tokens that exist within
    the language. This state is used to define the rule used to
    process the next character in the string.

    Characters that do not cause the state of the lexer to change
    should be appended to the end of the `buffer` attribute of
    the lexer.


    State Change
    ------------
    When the lexer encounters a character that represents the end of
    the previous token and the start of a new token, the state of
    the lexer changes. The specific details can vary based on the
    current state of the lexer, but by default the following occurs
    when the state is changed:

    *   A new TokenInfo object is created that contains the current
        state of the lexer and the current value of the `buffer`
        attribute of the lexer.
    *   That TokenInfo object is appended to the `tokens` attribute
        of the lexer.
    *   The `buffer` of the lexer is cleared.
    *   The `state` of the lexer is changed to the new state.
    *   The `process()` method is changed to the process method for
        the new state.


    `BaseLexer.process()` and Processing Methods
    --------------------------------------------
    The `process()` method of a BaseLexer subclass should not be
    defined. Instead the name should be assigned to a "processing"
    method specific to the current state of the lexer. By
    convention, the names of these method starts with an
    underscore, which is followed by the name of the state in
    lowercase letters. So the processing method for the state::

        Token.GROUP_OPEN

    would be::

        _group_open

    The signature for processing methods are::

        (self, char: str) -> None

    where `char` is the character being processed.

    While specific tokens may require different behavior, in general
    a processing method does two things:

    *   Define a list of states that are allowed to follow the
        current state within the syntax being lexed.
    *   pass that list and the character to the internal `_check_char()`
        method that handles the actual processing.

    The end result of calling a processing method is usually that
    the characters in the string that make up the symbol for the
    current state are stored in a "TokenInfo" tuple, which consists
    of the token representing the state and the characters of the
    symbol. These tokens will then be used by the parser to
    execute the command contained in the string.


    The State Map
    -------------
    To determine the correct processing method to use for a state, the
    lexer needs to have a mapping that defines the method for the state.
    This dictionary is the "state map." The tokens for the state are
    the keys, and the processing method for that state is the value
    for the key. This dictionary is passed into the BaseLexer as the
    `state_map` parameter when the lexer is initialized.


    The Symbol Map
    --------------
    A BaseLexer uses a "symbol map" to associate characters in the
    string to a state. The symbol map is a dictionary. The keys are
    the tokens from the enumeration that defines state. The values
    are a list of the strings that are allowed in that state. For
    example, if you have a token named "MULDIV" that is the state for
    multiplication and division operators, the symbol map might look
    like::

        >>> state_map = {
        >>>     Token.MULDIV: ['*', '/'],
        >>> }

    The symbol map is passed to the `symbol_map` parameter when the
    lexer is initialized.


    Bracketing
    ----------
    Instead of running each character through `_check_char()`, it is
    possible for a processing method to instead "bracket" characters
    until a specific character is reached. For example, characters
    after a quotation mark can be collected as a substring until
    the lexer hits another quotation mark.

    Why do this? The main use for this is to turn the bracketed
    substring into a single token, rather than three tokens: the
    opening bracket/delimiter, the content of the bracket, and the
    closing brack/delimiter.

    To expand on the quotation marks example above, let's characters
    surrounded by quotation marks to belong to a token called
    "QUALIFIER". We have the following enumeration of states and
    a `symbol_map` that defines which characters belong to which
    states::

        >>> from enum import auto, Enum
        >>> class Token(Enum):
        >>>     QUALIFIER = auto()
        >>>     DELIM = auto()
        >>>     QUALIFIER_END = auto()
        >>>
        >>> symbol_map = {
        >>>     Token.QUALIFIER: '',
        >>>     Token.DELIM: '"',
        >>>     QUALIFIER_END: '',
        >>> }

    The string we want to lex is::

        >>> text = '"spam"'

    Without a bracket state, you'd end up with a token list that
    would look like the following, assuming the logic for the
    QUALIFIER state is written to accept alphabetical characters
    as valid for qualifiers::

        >>> (
        >>>     (Token.DELIM, '"'),
        >>>     (Token.QUALIFER, 'spam'),
        >>>     (Token.DELIM, '"'),
        >>> )

    That's probably fine, but the delimiter tokens don't really
    do anything at this point. They were just there to set out
    the qualifier in the string. So, you can have them excluded
    from the token list like the following by using bracketing::

        >>> (
        >>>     (Token.QUALIFER, 'spam'),
        >>> )

    The real power here comes from combining with a result map
    to send the bracketed content of to a different lexer and
    parser, which allows syntaxes to be nested within each other.


    Bracket States
    --------------
    To have a processing method bracket, you need to associate
    the state for the opening bracket or delimiter with a
    processing method that handles the bracketing in a dictionary
    passed to the `bracket_states` parameter when initializing the
    BaseLexer. The `bracket_states` dictionary for the above example
    would look like this:

        >>> bracket_state = {
        >>>     Token.DELIM: Token.QUALIFIER,
        >>> }


    Bracket Ends
    ------------
    Because a bracket state hides the closing bracket or delimiter
    from the lexer, you need a different way to handle the state
    after a bracket state. This is handled by a standard processing
    method. By convention the name of this method is an underscore
    followed by the name of the bracket state followed by an
    underscore and then the word "end". For our example it would be::

        _qualifier_end

    This state needs to have a state token assigned for it. In our
    example that is the `Token.QUALIFIER_END` token.

    This end state then needs to be linked to the bracket state in
    a dictionary that is passed to the `bracket_ends` parameter
    when initializing the lexer. In the example, the `bracket_ends`
    dictionary would look like::

        bracket_ends = {
            Token.QUALIFIER: Token.QUALIFIER_END,
        }


    No Store
    --------
    Some states, like the initial state, bracket end states, and
    white space, shouldn't be stored as tokens. These are defined
    by the "no store" list, which is passed to the `no_store`
    parameter when the lexer is initialized. For the example above,
    the no store list could look like::

        >>> no_store = [
        >>>     Token.QUALIFIER_END,
        >>> ]


    Result Transformations
    ----------------------
    By default, a BaseLexer stores the symbols for the token as a
    string in the TokenInfo. This behavior can be changed with a
    "result transformation" method. By convention the name of a
    result transformation starts with an underscore, the letters "tf",
    an underscore, and the name of the state they affect in all lower
    case. So the name of a result transformation method for the
    `Token.NUMBER` state would be::

        _tf_number

    Result transformations have the following signature::

        (self, value:str) -> <type_of_the_transformed_value>

    .. warning:
        The return type of the result transformation method needs
        to be added to the types allowed for TokenInfo. This adds
        complexity that has downstream affects on the parser.

    In the case of something like `Token.NUMBER` the transformation
    can be very simple, coercing a string to an integer. However,
    more complex transformations are possible, such as sending
    bracketed symbols to a different lexer and parser to allow syntax
    nesting.


    Result Map
    ----------
    In order to link the result transformation methods to a state,
    a BaseLexer needs a "result map". The result map is a dictionary.
    The keys are the states where the transforms are used. The values
    are the result transformation methods to use for that state. For
    example, the result map for a lexer that transforms numbers and
    qualifiers might look like::

        >>> result_map = {
        >>>     Token.NUMBER: _tf_number,
        >>>     Token.QUALIFIER: _qualifier,
        >>> }

    The result map is passed to the `result_map` parameter when the
    BaseLexer is initialized.
    """
    def __init__(self,
                 state_map: dict[Token, Callable],
                 symbol_map: dict[Token, list[str]],
                 bracket_states: Optional[dict[Token, Token]] = None,
                 bracket_ends: Optional[dict[Token, Token]] = None,
                 result_map: Optional[dict[Token, Callable]] = None,
                 no_store: Optional[list[Token]] = None,
                 init_state: Token = Token.START) -> None:
        """Initialize an instance of :class:Lexer.

        :param state_map: A dictionary mapping the state of the lexer
            to the processing method for that state.
        :param symbol_map: A dictionary mapping states of the lexer to
            characters that could occur within the text being lexed.
        :param bracket_states: (Optional.) A dictionary mapping opening
            or delimiting states to a state that collects characters
            within the brackets or delimiters to send to a more
            specific lexer.
        :param bracket_ends: (Optional.) A dictionary mapping bracket
            states to a state that processes characters after the end
            of the bracket state.
        :param result_map: (Optional.) A dictionary mapping states
            to a result transformation method to transform the data
            in the lexed string before storing it in as a token
            value.
        :param no_store: (Optional.) A list of states that should not
            be stored as tokens.
        :param init_state: (Optional.) The initial state of the lexer.
            It defaults to :class:Token.START.
        :return: None.
        :rtype: NoneType
        """
        self.state_map = state_map
        self.symbol_map = symbol_map
        self.bracket_states = _mutable(bracket_states, dict)
        self.bracket_ends = _mutable(bracket_ends, dict)
        self.result_map = _mutable(result_map, dict)
        self.no_store = _mutable(no_store)
        self.init_state = init_state
        self.state = init_state

        self.process = self._start
        self.buffer = ''
        self.tokens: list[TokenInfo] = []

    # Public methods.
    def lex(self, yadn: str) -> tuple[TokenInfo, ...]:
        """Lex a dice notation string.

        :param yadn: A string of YADN representing a die roll. For
            details on YADN, see here: YADN_
        :return: A :class:tuple object.
        :rtype: tuple

        .. _YADN: https://github.com/pji/yadr/blob/main/docs/dice_notation.rst
        """
        for char in yadn:
            self.process(char)
        else:
            self._change_state(self.init_state, '')
        return tuple(self.tokens)

    # Private operation method.
    def _is_token_start(self, token: Token, char: str) -> bool:
        """Is the given character the start of a new token."""
        valid = {s[0] for s in self.symbol_map[token]}
        return char in valid

    def _is_token_still(self, char: str) -> bool:
        """Is the given character still a part of the current token."""
        index = len(self.buffer)
        tokens = [t for t in self.symbol_map[self.state] if len(t) > index]
        if tokens:
            valid = {s[index] for s in tokens}
            return char in valid
        return False

    def _cannot_follow(self, char: str) -> None:
        """The character is not allowed by the current state."""
        state = self.state.name
        if state == 'WHITESPACE' and self.tokens:
            state = self.tokens[-1][0].name
        elif state == 'WHITESPACE':
            state = 'START'
        if state == 'QUALIFIER_END':
            state = 'QUALIFIER'
        if state == 'NUMBER' and self.buffer == '-':
            state = 'NEGATIVE_SIGN'

        if state == 'START':
            msg = f'Cannot start with {char}.'
        else:
            article = 'a'
            if state[0] in 'AEIOU':
                article = 'an'
            msg = f'{char} cannot follow {article} {state}.'

        raise ValueError(msg)

    def _change_state(self, new_state: Token, char: str) -> None:
        """Terminate the previous token and start a new one."""
        # Terminate and store the old token.
        if self.state not in self.no_store:
            value: Result = self.buffer
            if self.state in self.result_map:
                transform = self.result_map[self.state]
                value = transform(value)
            token_info = (self.state, value)
            self.tokens.append(token_info)

        # Set new state.
        self.buffer = char
        self.state = new_state
        self.process = self.state_map[new_state]

    def _check_char(self, char: str, can_follow: list) -> None:
        """Determine how to process a character."""
        new_state: Optional[Token] = None

        # If the character doesn't change the state, add it to the
        # buffer and stop processing.
        if self._is_token_still(char):
            self.buffer += char
            return None

        # Check to see if the character starts a token that is allowed
        # to follow the current token. Stop looking once you find one.
        for token in can_follow:
            if self._is_token_start(token, char):
                new_state = token
                break

        # If not, throw an exception. Since whitespace isn't a token in
        # YADN, an exception saying a character can't follow WHITESPACE
        # isn't useful. Therefore handle that case by looking at the
        # last stored token.
        else:
            self._cannot_follow(char)

        # Some tokens start a state that doesn't match the token.
        if new_state in self.bracket_states:
            new_state = self.bracket_states[new_state]

        # Catch an attempt to end a number when the only character is
        # negative sign.
        if new_state and self.state == Token.NUMBER and self.buffer == '-':
            self._cannot_follow(char)

        # If the state changed, change the state.
        if new_state:
            self._change_state(new_state, char)

    # Lexing rules.
    @abstractmethod
    def _start(self, char: str) -> None:
        """An abstract method for the processing method used for the
        initial state of the lexer.

        :param char: The character currently being lexed.
        :return: None
        :rtype: NoneType
        """
        # The tokens that are allowed to follow the current state.
        can_follow: list[Token] = []

        # Check to see if the current character causes the lexer
        # to change state.
        self._check_char(char, can_follow)

    def _whitespace(self, char: str) -> None:
        """Lex white space."""
        if char.isspace():
            return None
        prev_state = self.init_state
        if self.tokens:
            prev_state = self.tokens[-1][0]
        if prev_state in self.bracket_ends:
            prev_state = self.bracket_ends[prev_state]
        process = self.state_map[prev_state]
        process(char)
