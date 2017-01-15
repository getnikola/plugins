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

"""Parser for LaTeX inputs."""

from __future__ import unicode_literals

from . import tree, tokenizer

import nikola.utils
import re

LOGGER = nikola.utils.get_logger('compile_latex.parser', nikola.utils.STDERR_HANDLER)


# Some constants and helper functions
class _Level(object):
    Text = 10
    SubSubSection = 5
    SubSection = 4
    Section = 3
    Chapter = 2
    Everything = -1
    NO_LEVEL = -2

    @staticmethod
    def get_level(command):
        if command == "chapter":
            return _Level.Chapter
        elif command == "section":
            return _Level.Section
        elif command == "subsection":
            return _Level.SubSection
        elif command == "subsubsection":
            return _Level.SubSubSection
        else:
            return _Level.NO_LEVEL

    @staticmethod
    def create_object(level, title):
        if level == _Level.SubSubSection:
            return tree.SubSubSection(title)
        elif level == _Level.SubSection:
            return tree.SubSection(title)
        elif level == _Level.Section:
            return tree.Section(title)
        elif level == _Level.Chapter:
            return tree.Chapter(title)
        raise Exception("Unknown level '{}'!".format(level))


class ParseError(Exception):
    """Represent error while parsing."""

    def __init__(self, tokenstream, message, filename=None):
        """Create error in given token stream with message and optional filename."""
        template = ("{2}@{0}: {1}" if filename is not None else "{0}: {1}")
        super(ParseError, self).__init__(template.format(tokenstream.get_position(tokenstream.current_indices()[0]), message, filename))


class CommandInfo:
    """Represents information of a command."""

    def __init__(self, command_name, argument_count, eat_trailing_whitespace, default_arguments, accept_unknown_commands=False, url_mode=set()):
        """Create command information.

        command_name: name of command;
        argument_count: number of arguments;
        eat_trailing_whitespace: whether to eat trailing whitespace or not;
        default_arguments: list of default arguments;
        accept_unknown_commands: whether to accept unknown commands in arguments;
        url_mode: set of which arguments to process in URL mode.
        """
        self.command_name = command_name
        self.argument_count = argument_count
        self.eat_trailing_whitespace = eat_trailing_whitespace
        self.default_arguments = default_arguments
        self.accept_unknown_commands = accept_unknown_commands
        self.url_mode = url_mode


class EnvironmentInfo:
    """Represents information of an environment."""

    def __init__(self, environment_name, argument_count, eat_trailing_whitespace, default_arguments, accept_unknown_commands=False, url_mode=set()):
        """Create environment information.

        environment_name: name of environment;
        argument_count: number of arguments;
        eat_trailing_whitespace: whether to eat trailing whitespace or not;
        default_arguments: list of default arguments;
        accept_unknown_commands: whether to accept unknown commands in arguments;
        url_mode: set of which arguments to process in URL mode.
        """
        self.environment_name = environment_name
        self.argument_count = argument_count
        self.eat_trailing_whitespace = eat_trailing_whitespace
        self.default_arguments = default_arguments
        self.accept_unknown_commands = accept_unknown_commands
        self.url_mode = url_mode


# Simple string replacement commands.
_replacement_commands = {
    'ldots': '\u2026',
    'vdots': '\u22EE',
    'cdots': '\u22EF',
}


class ParsingEnvironment(object):
    """Environmental data for parsing, like registered commands and environments."""

    languages = {
        'albanian': { 'locale': 'sq', },
        #'amharic': { 'locale': 'am', },
        'arabic': { 'locale': 'ar', 'right_to_left': True, },
        'armenian': { 'locale': 'hy', },
        # 'asturian': { 'locale': 'ast', },
        # 'bahasai': { 'locale': '', },
        # 'bahasam': { 'locale': '', },
        'basque': { 'locale': 'eu', },
        # 'bengali': { 'locale': 'bn', },
        'brazil': { 'locale': 'pt-br', },
        'brazilian': { 'locale': 'pt-br', },
        'breton': { 'locale': 'br', },
        'bulgarian': { 'locale': 'bg', },
        'catalan': { 'locale': 'ca', },
        # 'coptic': { 'locale': 'cop', },
        'croatian': { 'locale': 'hr', },
        'czech': { 'locale': 'cs', },
        'danish': { 'locale': 'da', },
        # 'divehi': { 'locale': '', },
        'dutch': { 'locale': 'nl', },
        'english': { 'locale': 'en', },
        'esperanto': { 'locale': 'eo', },
        'estonian': { 'locale': 'et', },
        'farsi': { 'locale': 'fa', 'right_to_left': True, },
        'finnish': { 'locale': 'fr', },
        'french': { 'locale': 'fr', },
        'friulan': { 'locale': 'fur', },
        'galician': { 'locale': 'gl', },
        'german': { 'locale': 'de', },
        'greek': { 'locale': 'el', }
        'hebrew': { 'locale': 'he', 'right_to_left': True, },
        # 'hindi': { 'locale': 'hi', },
        'icelandic': { 'locale': 'is', },
        # 'interlingua': { 'locale': '', },
        'irish': { 'locale': 'ga', },
        'italian': { 'locale': 'it', },
        # 'kannada': { 'locale': 'kn', },
        # 'khmer': { 'locale': 'km', },
        # 'korean': { 'locale': 'ko', },
        # 'lao': { 'locale': 'lo', },
        'latin': { 'locale': 'la', },
        'latvian': { 'locale': 'lv', },
        'lithuanian': { 'locale': 'lt', },
        # 'lsorbian': { 'locale': '', },
        'magyar': { 'locale': 'hu', },
        # 'malayalam': { 'locale': 'ml', },
        # 'marathi': { 'locale': 'mr', },
        # 'nko': { 'locale': '', },
        'norsk': { 'locale': 'nb', },
        'nynorsk': { 'locale': 'nn', },
        'occitan': { 'locale': 'oc', },
        'piedmontese': { 'locale': 'pms', },
        'polish': { 'locale': 'pl', },
        'portuges': { 'locale': 'pt', },
        'romanian': { 'locale': 'ro', },
        'romansh': { 'locale': 'rm', },
        'russian': { 'locale': 'ru', },
        # 'samin': { 'locale': '', },
        # 'sanskrit': { 'locale': 'sa', },
        'scottish': { 'locale': 'sco', },
        'serbian': { 'locale': 'sr', },
        'slovak': { 'locale': 'sk', },
        'slovenian': { 'locale': 'sl', },
        'spanish': { 'locale': 'es', },
        'swedish': { 'locale': 'sv', },
        # 'syriac': { 'locale': 'syc', },
        # 'tamil': { 'locale': 'ta', },
        # 'telugu': { 'locale': 'te', },
        # 'thai': { 'locale': 'th', },
        # 'tibetan': { 'locale': '', },
        'turkish': { 'locale': 'tr', },
        'turkmen': { 'locale': 'tk', },
        'ukrainian': { 'locale': 'uk', },
        'urdu': { 'locale': 'ur', 'right_to_left': True, },
        # 'usorbian': { 'locale': '', },
        # 'vietnamese': { 'locale': 'vi', },
        'welsh': { 'locale': 'cy', },
    }

    def __init__(self):
        """Initialize default environment."""
        self.commands = {}
        self.environments = {}
        self.register_command("item", 0)
        self.register_command_WS("code", 1)
        self.register_command_WS("textbf", 1)
        self.register_command_WS("textit", 1)
        self.register_command_WS("texttt", 1)
        self.register_command_WS("emph", 1)
        self.register_command("newpar", 0)
        self.register_command("chapter", 1)
        self.register_command("section", 1)
        self.register_command("subsection", 1)
        self.register_command("subsubsection", 1)
        self.register_command_WS("href", 2, url_mode={0})
        self.register_command_WS("url", 1, url_mode={0})
        self.register_command_WS("label", 1)
        self.register_command_WS("ref", 2, None)
        self.register_command_WS("symbol", 1)
        self.register_command_WS("foreignlanguage", 2)
        self.register_command("qed", 0)
        self.register_command("includegraphics", 2, None, accept_unknown_commands=True)
        self.register_command("setlength", 2, accept_unknown_commands=True)
        self.register_command("noindent", 0)
        self.register_command("hline", 0)
        self.register_command("cline", 1)
        self.register_environment_WS("codelisting", 1)
        self.register_environment("definition", 1, None)
        self.register_environment("definitions", 1, None)
        self.register_environment("lemma", 1, None)
        self.register_environment("proposition", 1, None)
        self.register_environment("theorem", 1, None)
        self.register_environment("corollary", 1, None)
        self.register_environment("example", 1, None)
        self.register_environment("examples", 1, None)
        self.register_environment("remark", 1, None)
        self.register_environment("remarks", 1, None)
        self.register_environment("proof", 1, None)
        self.register_environment("align*", 0)
        self.register_environment("align", 0)
        self.register_environment("itemize", 0)
        self.register_environment("enumerate", 0)
        self.register_environment("tikzpicture", 1, None, accept_unknown_commands=True)
        self.register_environment("pstricks", 1, accept_unknown_commands=True)
        self.register_environment("blockquote", 0)
        self.register_environment("center", 0)
        self.register_environment("picturegroup", 0)
        self.register_environment("formulalist", 1, 1)
        self.register_environment("tabular", 1)
        for replacement in _replacement_commands.keys():
            self.register_command_WS(replacement, 0)

    def register_command(self, command_name, argument_count, *default_arguments, accept_unknown_commands=False, url_mode=set()):
        """Register a new command.

        command_name: name of command;
        argument_count: number of arguments;
        default_arguments: list of default arguments;
        accept_unknown_commands: whether to accept unknown commands in arguments;
        url_mode: set of which arguments to process in URL mode.
        """
        self.commands[command_name] = CommandInfo(command_name, argument_count, True, default_arguments, accept_unknown_commands=accept_unknown_commands, url_mode=url_mode)

    def register_command_WS(self, command_name, argument_count, *default_arguments, accept_unknown_commands=False, url_mode=set()):
        """Register a new command which does not eat trailing whitespace.

        command_name: name of command;
        argument_count: number of arguments;
        default_arguments: list of default arguments;
        accept_unknown_commands: whether to accept unknown commands in arguments;
        url_mode: set of which arguments to process in URL mode.
        """
        self.commands[command_name] = CommandInfo(command_name, argument_count, False, default_arguments, accept_unknown_commands=accept_unknown_commands, url_mode=url_mode)

    def register_environment(self, environment_name, argument_count, *default_arguments, accept_unknown_commands=False, url_mode=set()):
        """Register a new environment.

        environment_name: name of environment;
        argument_count: number of arguments;
        default_arguments: list of default arguments;
        accept_unknown_commands: whether to accept unknown commands in arguments;
        url_mode: set of which arguments to process in URL mode.
        """
        self.environments[environment_name] = EnvironmentInfo(environment_name, argument_count, True, default_arguments, accept_unknown_commands=accept_unknown_commands, url_mode=url_mode)

    def register_environment_WS(self, environment_name, argument_count, *default_arguments, accept_unknown_commands=False, url_mode=set()):
        """Register a new environment which does not eat trailing whitespace.

        environment_name: name of environment;
        argument_count: number of arguments;
        default_arguments: list of default arguments;
        accept_unknown_commands: whether to accept unknown commands in arguments;
        url_mode: set of which arguments to process in URL mode.
        """
        self.environments[environment_name] = EnvironmentInfo(environment_name, argument_count, False, default_arguments, accept_unknown_commands=accept_unknown_commands, url_mode=url_mode)


class Parser:
    """The LaTeX parser."""

    def __init__(self, input, parsing_environment, filename=None):
        """Create parser from input string and parsing environment."""
        self.tokens = tokenizer.TokenStream(input)
        self.parsing_environment = parsing_environment
        self.filename = filename

    def __expect(self, token, skip=True):
        if self.tokens.current_type() == token:
            if skip:
                self.tokens.skip_current()
        else:
            raise ParseError(self.tokens, "Expected {0}, but found {1}!".format(token, self.tokens.current()), filename=self.filename)

    def __command_name(self, command):
        if len(command) == 2:
            return "\\{0}".format(command[0])
        else:
            return "\\{0}{{{1}}}".format(command[0], command[1])

    def __flatten(self, block):
        if isinstance(block, tree.Block):
            while True:
                if len(block.elements) == 1 and isinstance(block.elements[0], tree.Block):
                    if type(block) == tree.Block:
                        block.elements[0].labels.extend(block.labels)
                        block = block.elements[0]
                    elif type(block.elements[0]) == tree.Block:
                        block.labels.extend(block.elements[0].labels)
                        block.elements = block.elements[0].elements
                    else:
                        block.elements[0] = self.__flatten(block.elements[0])
                        break
                else:
                    for i in range(len(block.elements)):
                        block.elements[i] = self.__flatten(block.elements[i])
                    break
        return block

    def __get_inline_code(self, code_type):
        code_type = code_type.recombine_as_text()
        end_token = None
        end_char = None
        skip_first_char = False
        if self.tokens.current_type() == tokenizer.Token.CurlyBraketOpen:
            end_token = tokenizer.Token.CurlyBraketClose
            start = self.tokens.current_indices()[1]
        elif self.tokens.current_type() == tokenizer.Token.SquareBraketOpen:
            end_token = tokenizer.Token.SquareBraketClose
            start = self.tokens.current_indices()[1]
        elif self.tokens.current_type() == tokenizer.Token.Text:
            end_char = self.tokens.current_value()[0]
            if end_char == '(':
                end_char = ')'
            skip_first_char = True
            start = self.tokens.current_indices()[0] + 1
        else:
            raise ParseError(self.tokens, "Invalid delimiter {} for inline code!".format(self.tokens.current()), filename=self.filename)
        while self.tokens.has_current():
            if self.tokens.current_type() == end_token:
                end = self.tokens.current_indices()[0]
                self.tokens.skip_current()
                break
            elif (self.tokens.current_type() == tokenizer.Token.Text or self.tokens.current_type() == tokenizer.Token.EscapedText) and end_char is not None:
                si = 0
                if skip_first_char:
                    si = 1
                    skip_first_char = False
                index = self.tokens.current_value().find(end_char, si)
                if index >= si:
                    end = self.tokens.current_indices()[0] + index
                    if self.tokens.current_type() == tokenizer.Token.EscapedText:
                        end += 1
                    if index == len(self.tokens.current_value()) - 1:
                        self.tokens.skip_current()
                    else:
                        self.tokens.set_value(0, self.tokens.current_value()[index + 1:])
                    break
            self.tokens.skip_current()
        return tree.Code(code_type, self.tokens.get_substring(start, end))

    def __get_formatting(self, command):
        if len(command) == 2 and command[0] in ["emph", "textbf", "textit", "texttt"]:
            if isinstance(command[1][0], tree.Words):
                result = command[1][0]
            else:
                result = tree.Words()
                if command[1][0] is not None:
                    result.words.append(command[1][0])
            if command[0] == "emph":
                result.formatting = "emphasize"
            elif command[0] == "textbf":
                result.formatting = "strong"
            elif command[0] == "textit":
                result.formatting = "strong"
            elif command[0] == "texttt":
                result.formatting = "teletype"
            return result
        else:
            return None

    def __get_includegraphics(self, command):
        url = command[1][0].recombine_as_text()
        args = dict()
        if command[1][1] is not None:
            for argPair in re.split("\s*,\s*", command[1][1].recombine_as_text().strip()):
                arg = argPair.split("=")
                assert len(arg) == 2
                args[arg[0].strip()] = arg[1].strip()
        return tree.IncludeGraphics(url, args)

    def __get_tikz_picture(self, command):
        start = self.tokens.current_indices()[0]
        while self.tokens.has_current():
            if self.tokens.current() == (tokenizer.Token.Command, "end") and self.tokens.peek_type(1) == tokenizer.Token.CurlyBraketOpen and self.tokens.peek(2) == (tokenizer.Token.Text, command[1]) and self.tokens.peek_type(3) == tokenizer.Token.CurlyBraketClose:
                stop = self.tokens.current_indices()[0]
                self.tokens.skip_current(4)
                break
            self.tokens.skip_current()
        content = self.tokens.get_substring(start, stop).strip()
        args = None
        if command[2][0] is not None:
            args = command[2][0].recombine_as_text().strip()
        return tree.TikzPicture(content, args)

    def __get_PSTricks_picture(self, command):
        start = self.tokens.current_indices()[0]
        while self.tokens.has_current():
            if self.tokens.current() == (tokenizer.Token.Command, "end") and self.tokens.peek_type(1) == tokenizer.Token.CurlyBraketOpen and self.tokens.peek(2) == (tokenizer.Token.Text, command[1]) and self.tokens.peek_type(3) == tokenizer.Token.CurlyBraketClose:
                stop = self.tokens.current_indices()[0]
                self.tokens.skip_current(4)
                break
            self.tokens.skip_current()
        content = self.tokens.get_substring(start, stop).strip()
        argsList = re.split("\s*,\s*", command[2][0].recombine_as_text().strip())
        args = dict()
        for entry in argsList:
            entry = entry.split("=")
            assert len(entry) == 2
            args[entry[0].strip()] = entry[1].strip()
        return tree.PSTricksPicture(content, args)

    def __parse_command_impl(self, cmd, env, is_environment, eat_trailing_whitespace, argument_count, default_arguments, accept_unknown_commands=False, math_mode=False, url_mode=set()):
        args = []

        # Adjust argument count
        argument_count -= len(default_arguments)

        # Scan default arguments
        found_default_arguments = []
        while len(found_default_arguments) < len(default_arguments):
            idx = 0
            while self.tokens.peek_type(idx) == tokenizer.Token.Whitespace:
                idx += 1
            if self.tokens.peek_type(idx) == tokenizer.Token.SquareBraketOpen:
                while idx > 0:
                    self.tokens.skip_current()
                    idx -= 1
                while self.tokens.current_type() in {tokenizer.Token.Whitespace, tokenizer.Token.Comment}:
                    self.tokens.skip_current()
                self.__expect(tokenizer.Token.SquareBraketOpen)
                found_default_arguments.append(self.__parse_words(math_mode=math_mode, delimiter=tokenizer.Token.SquareBraketClose, accept_unknown_commands=accept_unknown_commands, url_mode=idx in url_mode))
                self.__expect(tokenizer.Token.SquareBraketClose)
            else:
                break
        while len(found_default_arguments) < len(default_arguments):
            found_default_arguments.append(default_arguments[len(found_default_arguments)])

        # Scan other arguments
        while len(args) < argument_count:
            while self.tokens.current_type() in {tokenizer.Token.Whitespace, tokenizer.Token.Comment}:
                self.tokens.skip_current()
            self.__expect(tokenizer.Token.CurlyBraketOpen)
            args.append(self.__parse_words(math_mode=math_mode, delimiter=tokenizer.Token.CurlyBraketClose, accept_unknown_commands=accept_unknown_commands, url_mode=len(args) in url_mode))
            self.__expect(tokenizer.Token.CurlyBraketClose)

        if eat_trailing_whitespace:
            while self.tokens.current_type() in {tokenizer.Token.Whitespace, tokenizer.Token.Comment}:
                self.tokens.skip_current()
        else:
            while self.tokens.current_type() == tokenizer.Token.Comment:
                self.tokens.skip_current()

        # Add default arguments at end of usual arguments
        args.extend(found_default_arguments)

        if is_environment:
            return cmd, env, args
        else:
            return cmd, args

    def __parse_command(self, accept_unknown_commands, math_mode=False):
        self.__expect(tokenizer.Token.Command, False)
        cmd = self.tokens.current_value()
        is_environment = False
        if cmd == "begin" or cmd == "end":
            is_environment = True
        self.tokens.skip_current()

        # Determine number of arguments
        if is_environment:
            while self.tokens.current_type() in {tokenizer.Token.Whitespace, tokenizer.Token.Comment}:
                self.tokens.skip_current()
            self.__expect(tokenizer.Token.CurlyBraketOpen)
            env = self.tokens.current_value()
            self.__expect(tokenizer.Token.Text)
            self.__expect(tokenizer.Token.CurlyBraketClose)
            if env not in self.parsing_environment.environments:
                if accept_unknown_commands:
                    while self.tokens.current_type() in {tokenizer.Token.Whitespace, tokenizer.Token.Comment}:
                        self.tokens.skip_current()
                    return (cmd, env),
                raise ParseError(self.tokens, "Unknown environment '{}'!".format(env), filename=self.filename)
            envI = self.parsing_environment.environments[env]
            eat_trailing_whitespace = envI.eat_trailing_whitespace
            if cmd == "end":
                argument_count = 0
                default_arguments = []
                accept_unknown_commands = False
                url_mode = set()
            else:
                argument_count = envI.argument_count
                default_arguments = envI.default_arguments
                accept_unknown_commands = envI.accept_unknown_commands
                url_mode = envI.url_mode
        else:
            if cmd not in self.parsing_environment.commands:
                if accept_unknown_commands:
                    while self.tokens.current_type() in {tokenizer.Token.Whitespace, tokenizer.Token.Comment}:
                        self.tokens.skip_current()
                    return cmd,
                raise ParseError(self.tokens, "Unknown command '{}'!".format(cmd), filename=self.filename)
            cmdI = self.parsing_environment.commands[cmd]
            eat_trailing_whitespace = cmdI.eat_trailing_whitespace
            argument_count = cmdI.argument_count
            default_arguments = cmdI.default_arguments
            accept_unknown_commands = cmdI.accept_unknown_commands
            url_mode = cmdI.url_mode
            env = None

        return self.__parse_command_impl(cmd, env, is_environment, eat_trailing_whitespace, argument_count, default_arguments, accept_unknown_commands=accept_unknown_commands, math_mode=math_mode, url_mode=url_mode)

    def __postprocess_text(self, text):
        for f, t in [
            ("<<", "\u00AB"),
            (">>", "\u00BB"),
            ("---", "\u2014"),
            ("--", "\u2013"),
            ("``", "\u201C"),
            ("''", "\u201D"),
        ]:
            text = text.replace(f, t)
        return text

    def __add_language(self, element, language, inline=True):
        langdata = self.parsing_environment.languages.get(language)
        if langdata is None:
            raise Exception("Unknown language '{0}'!".format(language))
        return tree.Language(element, langdata.get('right_to_left', False), langdata['locale'], inline=inline)

    def __parse_symbol(self, code):
        try:
            code = int(code)
        except:
            raise ParseError(self.tokens, "Cannot interpret symbol '{0}'!".format(code), filename=self.filename)
        return tree.WordPart(chr(code))

    def __parse_words(self, math_mode, delimiter, accept_unknown_commands=False, table_mode=False, url_mode=False):
        current_words = tree.Words()
        current_word = None
        table_ended = False

        def add_to_current_word(part):
            nonlocal current_word
            if current_word is None:
                current_word = tree.Word()
            current_word.parts.append(part)

        while self.tokens.has_current():
            token = self.tokens.current_type()
            if token == tokenizer.Token.Whitespace:
                # Flush word
                if current_word is not None:
                    current_words.words.append(current_word)
                    current_word = None
                else:
                    current_words.words.append(tree.Word())
                self.tokens.skip_current()
            elif token == tokenizer.Token.NonbreakableWhitespace:
                add_to_current_word(tree.WordPart(" "))
                self.tokens.skip_current()
            elif token == tokenizer.Token.Comment:
                add_to_current_word(tree.Comment(self.tokens.current_value()))
                self.tokens.skip_current()
            elif token == tokenizer.Token.Text:
                add_to_current_word(tree.WordPart(self.__postprocess_text(self.tokens.current_value())))
                self.tokens.skip_current()
            elif token == tokenizer.Token.EscapedText:
                add_to_current_word(tree.WordPart(self.tokens.current_value(), escaped=True))
                self.tokens.skip_current()
            elif token == tokenizer.Token.Command:
                level = _Level.get_level(self.tokens.current_value())
                if level != _Level.NO_LEVEL:
                    raise ParseError(self.tokens, "Cannot process level-changing command during words parsing!", filename=self.filename)
                else:
                    # math_mode: "ignore" unknown commands and put as text into stream
                    command = self.__parse_command(math_mode or accept_unknown_commands, math_mode=math_mode)
                    form = self.__get_formatting(command)
                    if form is not None:
                        add_to_current_word(form)
                    if len(command) == 1:
                        if command[0] == "(":
                            formula = self.__read_formula((")",))
                            add_to_current_word(tree.Formula(formula))
                        elif command[0] == "[":
                            raise ParseError(self.tokens, "Display mode math not allowed during word parsing!", filename=self.filename)
                        elif command[0] == ")" or command[0] == "]":
                            raise ParseError(self.tokens, "Unexpected end of math mode!", filename=self.filename)
                        else:
                            text = "\\{0}".format(command[0])
                            if len(command) == 2:
                                text += "{{{0}}}".format(command[1].strip())
                            add_to_current_word(tree.WordPart(text + " "))
                    elif command[0] == "code":
                        add_to_current_word(self.__get_inline_code(command[1][0]))
                    elif command[0] == 'href':
                        add_to_current_word(tree.Link(command[1][0].recombine_as_text(reescape=False), link_text=command[1][1]))
                    elif command[0] == 'url':
                        add_to_current_word(tree.Link(command[1][0].recombine_as_text(reescape=False)))
                    elif command[0] == 'symbol':
                        add_to_current_word(self.__parse_symbol(command[1][0].recombine_as_text()))
                    elif command[0] == 'ref':
                        add_to_current_word(tree.Reference(command[1][0].recombine_as_text(), command[1][1]))
                    elif command[0] == 'includegraphics':
                        if math_mode:
                            raise ParseError(self.tokens, "\\includegraphics not allowed in math mode!", filename=self.filename)
                        add_to_current_word(self.__get_includegraphics(command))
                    elif command[0] == 'begin' and command[1] == 'tikzpicture':
                        add_to_current_word(self.__get_tikz_picture(command))
                    elif command[0] == 'begin' and command[1] == 'pstricks':
                        add_to_current_word(self.__get_PSTricks_picture(command))
                    elif command[0] == 'foreignlanguage':
                        add_to_current_word(self.__add_language(command[1][1], command[1][0].recombine_as_text()))
                    elif command[0] in _replacement_commands:
                        add_to_current_word(tree.WordPart(_replacement_commands[command[0]]))
                    else:
                        if len(command) == 2:
                            raise ParseError(self.tokens, "Command '{}' not allowed during words parsing!".format(command[0]), filename=self.filename)
                        elif command[0] == 'end':
                            if command[1] == 'tabular' and table_mode:
                                table_ended = True
                                break
                            raise ParseError(self.tokens, "Unexpected end of environment '{}'!".format(command[1]), filename=self.filename)
                        else:
                            raise ParseError(self.tokens, "Environment '{}' not allowed during words parsing!".format(command[1]), filename=self.filename)
            elif token == tokenizer.Token.InlineFormulaDelimiter:
                if math_mode:
                    raise ParseError(self.tokens, "Cannot start another formula inside an formula!", filename=self.filename)
                self.tokens.skip_current()
                formula = self.__read_formula(tokenizer.Token.InlineFormulaDelimiter)
                add_to_current_word(tree.Formula(formula))
            elif token == tokenizer.Token.DisplayFormulaDelimiter:
                raise ParseError(self.tokens, "Cannot process display-style formulae during words parsing!", filename=self.filename)
            elif token == tokenizer.Token.CurlyBraketOpen:
                self.tokens.skip_current()
                add_to_current_word(self.__parse_words(math_mode=math_mode, delimiter=tokenizer.Token.CurlyBraketClose, accept_unknown_commands=accept_unknown_commands, url_mode=url_mode))
                self.__expect(tokenizer.Token.CurlyBraketClose)
            elif token == delimiter:
                break
            elif token == tokenizer.Token.CurlyBraketClose:
                raise ParseError(self.tokens, "Unexpected closing curly braket during words parsing!", filename=self.filename)
            elif token == tokenizer.Token.SquareBraketOpen:
                add_to_current_word(tree.WordPart("["))
                self.tokens.skip_current()
            elif token == tokenizer.Token.SquareBraketClose:
                add_to_current_word(tree.WordPart("]"))
                self.tokens.skip_current()
            elif token == tokenizer.Token.DoubleNewLine:
                raise ParseError(self.tokens, "Cannot process paragraph break during words parsing!", filename=self.filename)
            elif table_mode and token in (tokenizer.Token.ForcedLineBreak, tokenizer.Token.TableColumnDelimiter):
                break
            elif math_mode and token in (tokenizer.Token.ForcedLineBreak, tokenizer.Token.TableColumnDelimiter):
                self.tokens.skip_current()  # ignore
            elif url_mode and token == tokenizer.Token.TableColumnDelimiter:
                add_to_current_word(tree.WordPart("&", escaped=True))
                self.tokens.skip_current()
            else:
                raise ParseError(self.tokens, "Cannot handle token {}!".format(token), filename=self.filename)
        # Flush word
        if current_word is not None:
            current_words.words.append(current_word)
            current_word = None
        else:
            if len(current_words.words) > 0 and len(current_words.words[-1].parts) > 0:
                current_words.words.append(tree.Word())
        if table_mode:
            return current_words, table_ended
        else:
            return current_words

    def __read_formula(self, delimiter):
        start = self.tokens.current_indices()[0]
        delimitedByEnvironmentEnd = (type(delimiter) == tuple)
        while self.tokens.has_current():
            stop = self.tokens.current_indices()[0]
            token = self.tokens.current_type()
            if not delimitedByEnvironmentEnd and token == delimiter:
                self.__expect(delimiter)
                break
            if token == tokenizer.Token.Command and delimitedByEnvironmentEnd:
                if len(delimiter) > 1 and self.tokens.current_value() == "end":
                    command = self.__parse_command(True, math_mode=True)
                    if len(command) != 1:
                        if command[1] == delimiter[1]:
                            break
                elif len(delimiter) == 1 and self.tokens.current_value() == delimiter[0]:
                    self.tokens.skip_current()
                    break
                else:
                    self.tokens.skip_current()
            elif token == tokenizer.Token.CurlyBraketOpen:
                self.tokens.skip_current()
                self.__parse_words(math_mode=True, delimiter=tokenizer.Token.CurlyBraketClose)
                self.__expect(tokenizer.Token.CurlyBraketClose)
            elif token == tokenizer.Token.CurlyBraketClose:
                raise ParseError(self.tokens, "Unexpected closing curly braket during formula!", filename=self.filename)
            else:
                self.tokens.skip_current()
        return self.tokens.get_substring(start, stop).strip()

    def __expect_empty__parse_block_result(self, res):
        if res is not None:
            if len(res) == 3:
                raise ParseError(self.tokens, "Unexpected \\end{{{0}}} in block!".format(res[1]), filename=self.filename)
            else:
                raise ParseError(self.tokens, "Unexpected \\{0} in block!".format(res[0]), filename=self.filename)

    def __get_picturegroup(self, command):
        result = tree.PictureGroup()
        while self.tokens.has_current():
            token = self.tokens.current_type()
            if token == tokenizer.Token.Command:
                value = self.tokens.current_value()
                if value == 'end':
                    command = self.__parse_command(False)
                    if command[1] != 'picturegroup':
                        raise ParseError(self.tokens, "Unexpected \\end{{{0}}} in picture group!".format(command[1]), filename=self.filename)
                    return result
                elif value == 'picture':
                    self.tokens.skip_current()
                    command = self.__parse_command_impl('picture', None, False, True, 2, [])
                    result.pictures.append((command[1][0], command[1][1]))
                else:
                    raise ParseError(self.tokens, "Unexpected \\{0} in picture group!".format(value), filename=self.filename)
            else:
                raise ParseError(self.tokens, "Unexpected token {0} in picture group!".format(token), filename=self.filename)

    def __get_formulalist(self, command):
        result = tree.FormulaList()
        while self.tokens.has_current():
            token = self.tokens.current_type()
            if token == tokenizer.Token.Command:
                value = self.tokens.current_value()
                if value == 'end':
                    command = self.__parse_command(False)
                    if command[1] != 'formulalist':
                        raise ParseError(self.tokens, "Unexpected \\end{{{0}}} in formula list!".format(command[1]), filename=self.filename)
                    return result
                elif value == 'formula':
                    self.tokens.skip_current()
                    command = self.__parse_command_impl('formula', None, False, True, 1, [])
                    result.formulae.append(command[1][0])
                else:
                    raise ParseError(self.tokens, "Unexpected \\{0} in formula list!".format(value), filename=self.filename)
            else:
                raise ParseError(self.tokens, "Unexpected token {0} in formula list!".format(token), filename=self.filename)

    def __parse_tabular_alignment(self, alignment):
        result = []
        left_border = False
        for c in alignment.recombine_as_text():
            if c == '|':
                if len(result) > 0:
                    result[-1].right_border = True
                else:
                    left_border = True
            elif c == 'l':
                result.append(tree.TabularAlign(tree.TabularAlignEnum.Left, left_border=left_border))
                left_border = False
            elif c == 'c':
                result.append(tree.TabularAlign(tree.TabularAlignEnum.Center, left_border=left_border))
                left_border = False
            elif c == 'r':
                result.append(tree.TabularAlign(tree.TabularAlignEnum.Right, left_border=left_border))
                left_border = False
            elif c == ' ':
                pass  # ignore
            else:
                raise ParseError(self.tokens, "Unknown tabular alignment character '{0}'!".format(c), filename=self.filename)
        return result

    def __parse_tabular_lines(self):
        result = []
        while self.tokens.has_current():
            token = self.tokens.current_type()
            if token == tokenizer.Token.Command:
                value = self.tokens.current_value()
                if value == 'hline':
                    self.tokens.skip_current()
                    result.append(None)
                elif value == 'cline':
                    command = self.__parse_command(False)
                    value = command[1][0].recombine_as_text()
                    value_split = value.split('-')
                    if len(value_split) != 2:
                        raise ParseError(self.tokens, "Cannot interpret '{}' as column range!".format(value), filename=self.filename)
                    start = int(value_split[0]) if value_split[0] else None
                    end = int(value_split[1]) if value_split[1] else None
                    if start is None and end is None:
                        result.append(None)
                    else:
                        result.append((start, end))
                else:
                    break
            elif token == tokenizer.Token.Whitespace:
                self.tokens.skip_current()  # ignore
            elif token == tokenizer.Token.Comment:
                self.tokens.skip_current()  # ignore
            else:
                break
        return result

    def __parse_block(self, destination_block, block_level, current_Level, insideEnv):
        # Read blocks into higher-level block
        current_block = None
        current_words = None
        current_word = None

        def flush_word():
            nonlocal current_word, current_words
            # Flush word
            if current_word is not None:
                if current_words is None:
                    current_words = tree.Words()
                current_words.words.append(current_word)
                current_word = None

        def flush_words():
            nonlocal current_words, current_block
            flush_word()
            # Flush words
            if current_words is not None:
                if current_block is None:
                    current_block = tree.Block()
                current_block.elements.append(current_words)
                current_words = None

        def flush_block():
            nonlocal current_block
            flush_words()
            # Flush block
            if current_block is not None:
                destination_block.elements.append(current_block)
                current_block = None

        def add_to_current_word(part):
            nonlocal current_word
            if current_word is None:
                current_word = tree.Word()
            current_word.parts.append(part)

        def add_to_current_block(part):
            nonlocal current_words, current_block
            flush_words()
            if current_block is None:
                current_block = tree.Block()
            current_block.elements.append(part)

        while self.tokens.has_current():
            token = self.tokens.current_type()
            # print("Current block: " + str(current_block))
            # print("Current words: " + str(current_words))
            # print("Current word: " + str(current_word))
            # print(str(token))
            if token == tokenizer.Token.Whitespace:
                flush_word()
                self.tokens.skip_current()
            elif token == tokenizer.Token.NonbreakableWhitespace:
                add_to_current_word(tree.WordPart(" "))
                self.tokens.skip_current()
            elif token == tokenizer.Token.Comment:
                add_to_current_word(tree.Comment(self.tokens.current_value()))
                self.tokens.skip_current()
            elif token == tokenizer.Token.Text:
                add_to_current_word(tree.WordPart(self.__postprocess_text(self.tokens.current_value())))
                self.tokens.skip_current()
            elif token == tokenizer.Token.EscapedText:
                add_to_current_word(tree.WordPart(self.tokens.current_value(), escaped=True))
                self.tokens.skip_current()
            elif token == tokenizer.Token.Command:
                level = _Level.get_level(self.tokens.current_value())
                if level != _Level.NO_LEVEL:
                    if insideEnv:
                        raise ParseError(self.tokens, "Cannot start new block level inside an environment!", filename=self.filename)
                    # If we want to start a level which is as high as the block level or higher, we need to quit this function first
                    if level <= block_level:
                        break
                    # Now compare the level to the current level
                    if level > current_Level:
                        flush_words()
                        # add as child
                        command = self.__parse_command(False)
                        new_block = _Level.create_object(level, command[1][0])
                        res = self.__parse_block(new_block, level, level, False)
                        self.__expect_empty__parse_block_result(res)
                        if current_block is None:
                            current_block = tree.Block()
                        current_block.elements.append(new_block)
                    else:
                        flush_block()
                        # Add on same level
                        command = self.__parse_command(False)
                        new_block = _Level.create_object(level, command[1][0])
                        res = self.__parse_block(new_block, level, level, False)
                        self.__expect_empty__parse_block_result(res)
                        destination_block.elements.append(new_block)
                        current_Level = level
                else:
                    if self.tokens.current_value() == "(":
                        self.tokens.skip_current()
                        formula = self.__read_formula((")",))
                        add_to_current_word(tree.Formula(formula))
                    elif self.tokens.current_value() == "[":
                        self.tokens.skip_current()
                        self.tokens.skip_current()
                        formula = self.__read_formula(("]",))
                        add_to_current_block(tree.DisplayFormula(formula))
                    elif self.tokens.current_value() == ")" or self.tokens.current_value() == "]":
                        raise ParseError(self.tokens, "Unexpected end of math mode!", filename=self.filename)
                    else:
                        command = self.__parse_command(False)
                        form = self.__get_formatting(command)
                        if form is not None:
                            add_to_current_word(form)
                        elif len(command) == 3:
                            # environment
                            if command[0] == "end":
                                flush_block()
                                return command
                            if command[1] in {"definition", "definitions", "lemma", "proposition", "theorem", "corollary", "example", "examples", "remark", "remarks", "proof"}:
                                # Add on same level
                                new_block = tree.TheoremEnvironment(command[1])
                                if command[2][0] is not None:
                                    new_block.optional_title = command[2][0]
                                res = self.__parse_block(new_block, current_Level, current_Level, False)
                                if res is None:
                                    raise ParseError(self.tokens, "Unexpected end of '{}' environment!".format(command[1]), filename=self.filename)
                                if len(res) != 3:
                                    self.__expect_empty__parse_block_result(res)
                                if res[1] != command[1]:
                                    raise ParseError(self.tokens, "{0} paired with {1}!".format(self.__command_name(command), self.__command_name(res)), filename=self.filename)
                                add_to_current_block(new_block)
                            elif command[1] in ['blockquote', 'center']:
                                # Add on same level
                                new_block = tree.SpecialBlock(command[1])
                                res = self.__parse_block(new_block, current_Level, current_Level, False)
                                if res is None:
                                    raise ParseError(self.tokens, "Unexpected end of '{}' environment!".format(command[1]), filename=self.filename)
                                if len(res) != 3:
                                    self.__expect_empty__parse_block_result(res)
                                if res[1] != command[1]:
                                    raise ParseError(self.tokens, "{0} paired with {1}!".format(self.__command_name(command), self.__command_name(res)), filename=self.filename)
                                add_to_current_block(new_block)
                            elif command[1] in {"align*", "align"}:
                                formula = self.__read_formula(command)
                                # Add display formula
                                add_to_current_block(tree.AlignFormula(formula))
                            elif command[1] in {"itemize", "enumerate"}:
                                if command[1] == "itemize":
                                    enumType = "ul"
                                else:
                                    enumType = "ol"
                                enum = tree.Enumeration(enumType)
                                # Parse first "item"
                                item_command = self.__parse_command(False)
                                if len(item_command) != 2 or item_command[0] != 'item':
                                    raise ParseError(self.tokens, "Expected \\item, but got {}".format(self.__command_name(item_command)), filename=self.filename)
                                while True:
                                    new_block = tree.Block()
                                    res = self.__parse_block(new_block, _Level.Text, _Level.Text, False)
                                    if len(new_block.elements) == 1:
                                        enum.elements.append(new_block.elements[0])
                                    else:
                                        enum.elements.append(new_block)
                                    # Check for result
                                    if res is None:
                                        raise ParseError(self.tokens, "Unexpected end of '{}' environment!".format(command[1]), filename=self.filename)
                                    if len(res) == 2 and res[0] == "item":
                                        continue
                                    if len(res) == 3 and res[1] == command[1] and res[0] == 'end':
                                        break
                                    if len(res) == 3 and res[1] != command[1]:
                                        raise ParseError(self.tokens, "{0} paired with {1}!".format(self.__command_name(command), self.__command_name(res)), filename=self.filename)
                                    self.__expect_empty__parse_block_result(res)
                                add_to_current_block(enum)
                            elif command[1] == "codelisting":
                                flush_block()
                                # Extract code
                                start = self.tokens.current_indices()[0]
                                while self.tokens.has_current():
                                    if self.tokens.current() == (tokenizer.Token.Command, "end") and self.tokens.peek_type(1) == tokenizer.Token.CurlyBraketOpen and self.tokens.peek(2) == (tokenizer.Token.Text, "codelisting") and self.tokens.peek_type(3) == tokenizer.Token.CurlyBraketClose:
                                        stop = self.tokens.current_indices()[0]
                                        self.tokens.skip_current(4)
                                        break
                                    self.tokens.skip_current()
                                destination_block.elements.append(tree.CodeBlock(command[2][0].recombine_as_text(), self.tokens.get_substring(start, stop).strip(" ").strip("\n")))
                            elif command[1] == 'tikzpicture':
                                add_to_current_word(self.__get_tikz_picture(command))
                            elif command[1] == 'pstricks':
                                add_to_current_word(self.__get_PSTricks_picture(command))
                            elif command[1] == 'picturegroup':
                                add_to_current_block(self.__get_picturegroup(command))
                            elif command[1] == 'formulalist':
                                add_to_current_block(self.__get_formulalist(command))
                            elif command[1] == 'tabular':
                                tabular = tree.Tabular(self.__parse_tabular_alignment(command[2][0]))
                                tabular.add_lines(self.__parse_tabular_lines())
                                while True:
                                    cell, table_ended = self.__parse_words(math_mode=False, delimiter=None, table_mode=True)
                                    tabular.add_cell(cell)
                                    if table_ended:
                                        break
                                    token = self.tokens.current_type()
                                    if token == tokenizer.Token.ForcedLineBreak:
                                        tabular.next_row()
                                        self.tokens.skip_current()
                                        tabular.add_lines(self.__parse_tabular_lines())
                                    elif token == tokenizer.Token.TableColumnDelimiter:
                                        self.tokens.skip_current()
                                    else:
                                        raise ParseError(self.tokens, "Unexpected {0} token in tabular environment!".format(token), filename=self.filename)
                                tabular.end_of_table_parsing()
                                add_to_current_word(tabular)
                            else:
                                raise ParseError(self.tokens, "Unknown environment start {}!".format(self.__command_name(command)), filename=self.filename)
                        else:
                            # command
                            if command[0] == 'newpar':
                                flush_words()
                            elif command[0] == 'item':
                                flush_block()
                                return command
                            elif command[0] == 'noindent':
                                pass  # ignore
                            elif command[0] == 'setlength':
                                pass  # ignore
                            elif command[0] == "code":
                                add_to_current_word(self.__get_inline_code(command[1][0]))
                            elif command[0] == 'href':
                                add_to_current_word(tree.Link(command[1][0].recombine_as_text(reescape=False), link_text=command[1][1]))
                            elif command[0] == 'url':
                                add_to_current_word(tree.Link(command[1][0].recombine_as_text(reescape=False)))
                            elif command[0] == 'symbol':
                                add_to_current_word(self.__parse_symbol(command[1][0].recombine_as_text()))
                            elif command[0] == 'ref':
                                add_to_current_word(tree.Reference(command[1][0].recombine_as_text(), command[1][1]))
                            elif command[0] == 'qed':
                                if isinstance(destination_block, tree.TheoremEnvironment):
                                    destination_block.qed = True
                            elif command[0] == 'label':
                                destination_block.labels.append(command[1][0].recombine_as_text())
                            elif command[0] == 'includegraphics':
                                add_to_current_word(self.__get_includegraphics(command))
                            elif command[0] == 'foreignlanguage':
                                add_to_current_word(self.__add_language(command[1][1], command[1][0].recombine_as_text()))
                            elif command[0] in _replacement_commands:
                                add_to_current_word(tree.WordPart(_replacement_commands[command[0]]))
                            else:
                                raise ParseError(self.tokens, "Unsupported command '{}'!".format(command[0]), filename=self.filename)
            elif token == tokenizer.Token.InlineFormulaDelimiter:
                self.tokens.skip_current()
                formula = self.__read_formula(tokenizer.Token.InlineFormulaDelimiter)
                add_to_current_word(tree.Formula(formula))
            elif token == tokenizer.Token.DisplayFormulaDelimiter:
                self.tokens.skip_current()
                formula = self.__read_formula(tokenizer.Token.DisplayFormulaDelimiter)
                add_to_current_block(tree.DisplayFormula(formula))
            elif token == tokenizer.Token.CurlyBraketOpen:
                self.tokens.skip_current()
                add_to_current_word(self.__parse_words(math_mode=False, delimiter=tokenizer.Token.CurlyBraketClose))
                self.__expect(tokenizer.Token.CurlyBraketClose)
            elif token == tokenizer.Token.CurlyBraketClose:
                raise ParseError(self.tokens, "Unexpected closing curly braket!", filename=self.filename)
            elif token == tokenizer.Token.SquareBraketOpen:
                add_to_current_word(tree.WordPart("["))
                self.tokens.skip_current()
            elif token == tokenizer.Token.SquareBraketClose:
                add_to_current_word(tree.WordPart("]"))
                self.tokens.skip_current()
            elif token == tokenizer.Token.DoubleNewLine:
                flush_words()
                self.tokens.skip_current()
            else:
                raise ParseError(self.tokens, "Cannot handle token {}!".format(token), filename=self.filename)

        flush_block()
        return None

    def parse(self):
        """Do parsing."""
        block = tree.Block()
        res = self.__parse_block(block, _Level.Everything, _Level.Text, False)
        self.__expect_empty__parse_block_result(res)
        block = self.__flatten(block)
        return block


def parse(input, parsing_environment, filename=None):
    """Create parser object and execute parsing.

    ``input``: unicode input string;
    ``parsing_environment``: instance of ``ParsingEnvironment``;
    ``filename``: optional filename to be used in error messages.
    """
    parser = Parser(input, parsing_environment, filename=filename)
    return parser.parse()
