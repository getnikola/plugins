# -*- coding: utf-8 -*-

# Copyright © 2014-2017 Felix Fontein
#
# Permission is hereby granted, free of charge, to any
# person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the
# Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the
# Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice
# shall be included in all copies or substantial portions of
# the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
# KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
# PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS
# OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""A basic LaTeX tokenizer."""

from __future__ import unicode_literals

import nikola.utils

from enum import Enum

LOGGER = nikola.utils.get_logger('compile_latex.tokenizer', nikola.utils.STDERR_HANDLER)


class Token(Enum):
    """Represents a single token."""

    Whitespace = 1
    NonbreakableWhitespace = 2
    Text = 3
    EscapedText = 4
    Command = 5  # '\' followed by text
    InlineFormulaDelimiter = 6  # just '$' (the alternative, '\(', is a Command)
    DisplayFormulaDelimiter = 7  # just '$$' (the alternative, '\[', is a Command)
    CurlyBraketOpen = 8  # '{'
    CurlyBraketClose = 9  # '}'
    SquareBraketOpen = 10  # '['
    SquareBraketClose = 11  # ']'
    DoubleNewLine = 12
    Comment = 13  # '%'
    ForcedLineBreak = 14  # '\\'
    TableColumnDelimiter = 15  # '&'


def _compute_position(input, index):
    """Compute line/column position given an index in a string."""
    line = 1
    col = 1
    eol = None  # last end of line character
    for c in input[:index]:
        if c == '\n' or c == '\r':
            if eol is None or eol == c:
                eol = c
                line += 1
                col = 1
            else:
                # ignore second of '\n\r' and '\r\n' sequences
                eol = None
        else:
            col += 1
    return (line, col)


class Tokenizer:
    """A simple tokenizer."""

    def _is_whitespace(self, char):
        """Check for whitespace."""
        return ord(char) <= 32

    def _is_line_break(self, char):
        """Check for line breaks."""
        return ord(char) == 10 or ord(char) == 13

    def _is_command_char(self, char):
        """Check for a command character."""
        return (char >= 'A' and char <= 'Z') or (char >= 'a' and char <= 'z') or (char == '@')

    def _eat_whitespace(self):
        """Skip whitespace and return number of contained line breaks."""
        number_of_line_breaks = 0
        last_line_break = None
        while self._position < len(self._input):
            if not self._is_whitespace(self._input[self._position]):
                break
            if self._is_line_break(self._input[self._position]):
                if last_line_break is None or last_line_break == self._input[self._position]:
                    number_of_line_breaks += 1
                last_line_break = self._input[self._position]
            else:
                last_line_break = None
            self._position += 1
        return number_of_line_breaks

    def _eat_comment(self):
        """Skip comment's content."""
        start = self._position
        last_line_break = None
        had_line_break = False
        while self._position < len(self._input):
            if had_line_break and not self._is_whitespace(self._input[self._position]):
                break
            if self._is_line_break(self._input[self._position]):
                if last_line_break is None or last_line_break == self._input[self._position]:
                    if had_line_break:
                        break
                last_line_break = self._input[self._position]
                had_line_break = True
            else:
                last_line_break = None
            self._position += 1
        return self._input[start:self._position]

    def _read_text(self, strict):
        """Read text."""
        start = self._position
        while self._position < len(self._input):
            char = self._input[self._position]
            if self._is_whitespace(char):
                break
            if char == "~" or char == "{" or char == "}" or char == "$" or char == "[" or char == "]" or char == "$" or char == "\\" or char == "&":
                break
            if strict and not self._is_command_char(char):
                break
            self._position += 1
        return self._input[start:self._position]

    def _find_next(self):
        """Find next token."""
        self._token = None
        self._token_value = None
        self._token_begin_index = None
        self._token_end_index = None
        if (self._position >= len(self._input)):
            return
        self._token_begin_index = self._position
        char = self._input[self._position]
        if self._is_whitespace(char):
            number_of_line_breaks = self._eat_whitespace()
            if number_of_line_breaks > 1:
                self._token = Token.DoubleNewLine
            else:
                self._token = Token.Whitespace
        elif char == "~":
            self._token = Token.NonbreakableWhitespace
            self._position += 1
        elif char == '&':
            self._token = Token.TableColumnDelimiter
            self._position += 1
        elif char == "{":
            self._token = Token.CurlyBraketOpen
            self._position += 1
        elif char == "}":
            self._token = Token.CurlyBraketClose
            self._position += 1
        elif char == "[":
            self._token = Token.SquareBraketOpen
            self._position += 1
        elif char == "]":
            self._token = Token.SquareBraketClose
            self._position += 1
        elif char == "$":
            self._token = Token.InlineFormulaDelimiter
            self._position += 1
            if self._position < len(self._input) and self._input[self._position] == "$":
                self._token = Token.DisplayFormulaDelimiter
                self._position += 1
        elif char == "\\":
            self._position += 1
            if self._position == len(self._input):
                raise "Reached end of text after '\\'"
            self._token = Token.Command
            cmd = self._read_text(True)
            if len(cmd) == 0:
                ch = self._input[self._position]
                if ch == '(' or ch == ')' or ch == '[' or ch == ']':
                    self._token_value = ch
                elif ch == '\\':
                    self._token = Token.ForcedLineBreak
                else:
                    self._token = Token.EscapedText
                    self._token_value = ch
                self._position += 1
            else:
                self._token_value = cmd
        elif char == '%':
            self._token = Token.Comment
            self._position += 1
            self._token_value = self._eat_comment()
        else:
            self._token = Token.Text
            self._token_value = self._read_text(False)
        self._token_end_index = self._position

    def __init__(self, input):
        """Initialize tokenizer with input unicode string ``input``."""
        self._input = input
        self._position = 0
        self._find_next()

    def has_token(self):
        """Whether a token is available."""
        return self._token is not None

    def token_type(self):
        """Return type of current token."""
        return self._token

    def token_value(self):
        """Return value of current token."""
        # only if token_type() returns Token.Text or Token.Command
        return self._token_value

    def token_begin_index(self):
        """Return beginning of token in input string."""
        return self._token_begin_index

    def token_end_index(self):
        """Return end of token in input string."""
        return self._token_end_index

    def next(self):
        """Proceed to next token."""
        if self._token is not None:
            self._find_next()

    def get_substring(self, start_index, end_index):
        """Return substring of input string."""
        return self._input[start_index:end_index]

    def get_position(self, index):
        """Retrieve position as (line, column) pair in input string."""
        return _compute_position(self._input, index)


class TokenStream:
    """Represent the output of a Tokenizer as a stream of tokens, allowing to peek ahead."""

    def _fill_ahead(self, count):
        """Fill ahead buffer."""
        if len(self.__ahead) < count:
            for i in range(len(self.__ahead), count):
                if self.__tokenizer.has_token():
                    self.__ahead.append((self.__tokenizer.token_type(), self.__tokenizer.token_value()))
                    self.__ahead_indices.append((self.__tokenizer.token_begin_index(), self.__tokenizer.token_end_index()))
                    self.__tokenizer.next()
                else:
                    self.__ahead.append((None, None))
                    self.__ahead_indices.append((None, None))

    def __init__(self, input):
        """Create TokenStream from input unicode string. Creates Tokenizer."""
        self.__tokenizer = Tokenizer(input)
        self.__ahead = list()
        self.__ahead_indices = list()

    def current(self):
        """Get current token. Return pair (type, value)."""
        self._fill_ahead(1)
        return self.__ahead[0]

    def current_indices(self):
        """Get current token indices in input string."""
        self._fill_ahead(1)
        return self.__ahead_indices[0]

    def current_type(self):
        """Get current token type."""
        self._fill_ahead(1)
        return self.__ahead[0][0]

    def current_value(self):
        """Get current token value."""
        self._fill_ahead(1)
        return self.__ahead[0][1]

    def has_current(self):
        """Return True if current token is available."""
        self._fill_ahead(1)
        return self.__ahead[0][0] is not None

    def skip_current(self, count=1):
        """Skip number of tokens."""
        assert count >= 0
        self._fill_ahead(count)
        self.__ahead = self.__ahead[count:]
        self.__ahead_indices = self.__ahead_indices[count:]

    def peek(self, index):
        """Peek ahead in token stream. Return pair (type, value)."""
        assert index >= 0
        self._fill_ahead(index + 1)
        return self.__ahead[index]

    def peek_indices(self, index):
        """Peek ahead in token stream. Return indices of token in input string."""
        assert index >= 0
        self._fill_ahead(index + 1)
        return self.__ahead_indices[index]

    def peek_type(self, index):
        """Peek ahead in token stream. Return token's type."""
        assert index >= 0
        self._fill_ahead(index + 1)
        return self.__ahead[index][0]

    def peek_value(self, index):
        """Peek ahead in token stream. Return token's value."""
        assert index >= 0
        self._fill_ahead(index + 1)
        return self.__ahead[index][1]

    def can_peek(self, index):
        """Check whether token at current index + ``index`` can be peeked at, i.e. whether it exists."""
        assert index >= 0
        self._fill_ahead(index + 1)
        return self.__ahead[index][0] is not None

    def get_substring(self, start_index, end_index):
        """Return substring of input string."""
        return self.__tokenizer.get_substring(start_index, end_index)

    def get_position(self, index):
        """Retrieve position as (line, column) pair in input string."""
        return self.__tokenizer.get_position(index)

    def set_value(self, index, new_value):
        """Set value of token at current index + ``index`` to ``new_value``.

        Use with care!
        """
        assert index >= 0
        self._fill_ahead(index + 1)
        self.__ahead[index] = (self.__ahead[index][0], new_value)


def recombine_tokens(tokens):
    """Recombine list of tokens as string."""
    result = ""
    for type, value in tokens:
        if type == Token.Whitespace:
            result += " "
        if type == Token.NonbreakableWhitespace:
            result += "~"
        elif type == Token.Text:
            result += value
        elif type == Token.EscapedText:
            result += "\\{}".format(value)
        elif type == Token.Command:
            result += "\\{}".format(value)
        elif type == Token.InlineFormulaDelimiter:
            result += "$"
        elif type == Token.DisplayFormulaDelimiter:
            result += "$$"
        elif type == Token.CurlyBraketOpen:
            result += "{"
        elif type == Token.CurlyBraketClose:
            result += "}"
        elif type == Token.SquareBraketOpen:
            result += "["
        elif type == Token.SquareBraketClose:
            result += "]"
        elif type == Token.DoubleNewLine:
            result += "\n\n"
    return result
