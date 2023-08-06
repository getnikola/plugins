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

"""Provides primitives for representing a LaTeX tree and for processing it."""

from __future__ import unicode_literals

from enum import Enum


def _is_whitespace_and_comments(root):
    """Check whether the subtree beginning at root only represents whitespace and comments."""
    if isinstance(root, WordPart):
        return len(root.text) == 0
    elif isinstance(root, Word):
        for part in root.parts:
            if not _is_whitespace_and_comments(part):
                return False
        return True
    elif isinstance(root, Comment):
        return True
    elif isinstance(root, Words):
        if root.formatting is not None:
            return False
        for word in root.words:
            if not _is_whitespace_and_comments(word):
                return False
        return True
    else:
        return False


class Base:
    """The base object."""

    def __str__(self):
        """Generate textual representation."""
        return "Base()"

    def __repr__(self):
        """Generate textual representation by calling __str__."""
        return str(self)

    def recombine_as_text(self, reescape=True):
        """Recombine subtree as LaTeX source text."""
        return ""

    def print(self, indent):
        """Print to stdout with given indentation."""
        print("  " * indent + str(self))

    def visit(self, visitor, *args, **kw):
        """Process with TreeVisitor object. Passes ``args`` and ``kw`` to the corresponding method of ``visitor``."""
        raise NotImplementedError()


class Language(Base):
    """Represents a subtree with a different language."""

    def __init__(self, element, right_to_left, locale, inline=False):
        """Initialize object.

        ``element`` is the content;
        ``right_to_left`` is a boolean whether this is for a left-to-right language;
        ``locale`` is the locale of the language;
        ``inline`` is a boolean whether this is an inline or block level element.
        """
        self.element = element
        self.right_to_left = right_to_left
        self.locale = locale
        self.inline = inline

    def __str__(self):
        """Generate textual representation."""
        return "Language({}[{}]{}: {})".format(self.locale, 'rtl' if self.right_to_left else 'ltr', ', inline' if self.inline else '', self.element)

    def recombine_as_text(self, reescape=True):
        """Recombine subtree as LaTeX source text."""
        return "{{{0}}}".format(self.element)

    def visit(self, visitor, *args, **kw):
        """Process with TreeVisitor object. Passes ``args`` and ``kw`` to the corresponding method of ``visitor``."""
        return visitor.process_language(self, *args, **kw)


class Comment(Base):
    """Represents a comment."""

    def __init__(self, text):
        """Initialize object."""
        self.text = text

    def __str__(self):
        """Generate textual representation."""
        return "Comment({})".format(self.text)

    def recombine_as_text(self, reescape=True):
        """Recombine subtree as LaTeX source text."""
        return "%{0}".format(self.text)

    def visit(self, visitor, *args, **kw):
        """Process with TreeVisitor object. Passes ``args`` and ``kw`` to the corresponding method of ``visitor``."""
        return visitor.process_comment(self, *args, **kw)


class TabularAlignEnum(Enum):
    """Describe the alignment of a table cell."""

    Left = 1
    Center = 2
    Right = 3


class TabularAlign(object):
    """Represents information on the alignment of cells of a table."""

    def __init__(self, align, left_border=False, right_border=False):
        """Initialize object."""
        self.align = align
        self.left_border = left_border
        self.right_border = right_border

    def __str__(self):
        """Generate textual representation."""
        result = ''
        if self.left_border:
            result += '|'
        if self.align == TabularAlignEnum.Left:
            result += 'l'
        elif self.align == TabularAlignEnum.Center:
            result += 'c'
        elif self.align == TabularAlignEnum.Right:
            result += 'r'
        else:
            result += '?'
        if self.right_border:
            result += '|'
        return result


class Tabular(Base):
    """Represents a tabular environment."""

    def __init__(self, alignment):
        """Initialize object."""
        self.alignment = alignment
        self.current_row = None
        self.lines_data = []
        self.rows = []

    def __str__(self):
        """Generate textual representation."""
        alignment = ''.join([str(align) for align in self.alignment])
        content = "; ".join(["[{}]".format(", ".join(["{}".format(cell) for cell in row])) for row in self.rows])
        return "Tabular({}: {})".format(alignment, content)

    def recombine_as_text(self, reescape=True):
        """Recombine subtree as LaTeX source text."""
        result = [r"\begin{tabular}{"]
        for align in self.alignment:
            result.append(str(align))
        result.append(r"}\n")
        for i, row in enumerate(self.rows):
            for j, cell in enumerate(row):
                result.append(cell.recombine_as_text(reescape))
                if j + 1 < len(cell):
                    result.append(" & ")
            if i + 1 < len(self.rows):
                result.append(r'\\')
            result.append('\n')
        result.append(r"\end{tabular}")
        return ''.join(result)

    def add_cell(self, content):
        """Add a cell to the current row. During construction only."""
        if self.current_row is None:
            self.current_row = []
            self.rows.append(self.current_row)
        self.current_row.append(content)

    def next_row(self):
        """Proceed to a new row. During construction only."""
        if self.current_row is not None:
            self.current_row = None

    def add_lines(self, lines):
        """Add data on borders."""
        self.lines_data.append(lines)

    def end_of_table_parsing(self):
        """Signal end of construction phase."""
        if len(self.rows) > 0:
            last_row = self.rows[-1]
            if len(last_row) == 0:
                del self.rows[-1]
            elif len(last_row) == 1:
                if _is_whitespace_and_comments(last_row[0]):
                    del self.rows[-1]

    def visit(self, visitor, *args, **kw):
        """Process with TreeVisitor object. Passes ``args`` and ``kw`` to the corresponding method of ``visitor``."""
        return visitor.process_tabular(self, *args, **kw)


class IncludeGraphics(Base):
    r"""Represents a \includegraphics{} command."""

    def __init__(self, url, args):
        """Initialize object."""
        self.url = url
        self.args = args

    def recombine_as_text(self, reescape=True):
        """Recombine subtree as LaTeX source text."""
        result = r'\includegraphics'
        if len(self.args) > 0:
            result += '['
            first = True
            for key, value in self.args.items():
                if first:
                    first = False
                else:
                    result += ','
                result += str(key) + '=' + str(value)
            result += ']'
        return result + '{' + self.url + '}'

    def __str__(self):
        """Generate textual representation."""
        return "Image(" + self.url + "; " + str(self.args) + ")"

    def visit(self, visitor, *args, **kw):
        """Process with TreeVisitor object. Passes ``args`` and ``kw`` to the corresponding method of ``visitor``."""
        return visitor.process_include_graphics(self, *args, **kw)


class WordPart(Base):
    """Represents a part of a word."""

    def __init__(self, text, escaped=False):
        """Initialize object."""
        self.text = text
        self.escaped = escaped

    def recombine_as_text(self, reescape=True):
        """Recombine subtree as LaTeX source text."""
        if self.escaped and reescape:
            return '\\' + self.text
        else:
            return self.text

    def __str__(self):
        """Generate textual representation."""
        return "'" + self.text + "'"

    def visit(self, visitor, *args, **kw):
        """Process with TreeVisitor object. Passes ``args`` and ``kw`` to the corresponding method of ``visitor``."""
        return visitor.process_word_part(self, *args, **kw)


class Code(Base):
    """Represents a piece of code."""

    def __init__(self, type, code):
        """Initialize object."""
        self.type = type
        self.code = code

    def recombine_as_text(self, reescape=True):
        """Recombine subtree as LaTeX source text."""
        raise NotImplementedError()

    def __str__(self):
        """Generate textual representation."""
        return "Code('" + self.type + "', '" + self.code + "')"

    def visit(self, visitor, *args, **kw):
        """Process with TreeVisitor object. Passes ``args`` and ``kw`` to the corresponding method of ``visitor``."""
        return visitor.process_code_inline(self, *args, **kw)


class Formula(Base):
    """Represents a formula."""

    def __init__(self, formula):
        """Initialize object."""
        self.formula = formula

    def recombine_as_text(self, reescape=True):
        """Recombine subtree as LaTeX source text."""
        return "$" + self.formula + "$"

    def __str__(self):
        """Generate textual representation."""
        return "Formula(" + str(self.formula) + ")"

    def visit(self, visitor, *args, **kw):
        """Process with TreeVisitor object. Passes ``args`` and ``kw`` to the corresponding method of ``visitor``."""
        return visitor.process_inline_formula(self, *args, **kw)


class TikzPicture(Formula):
    """Represents a Tikz picture."""

    def __init__(self, formula, args):
        """Initialize object."""
        super(TikzPicture, self).__init__(formula)
        self.args = args

    def recombine_as_text(self, reescape=True):
        """Recombine subtree as LaTeX source text."""
        result = "\\begin{tikzpicture}"
        if self.args is not None:
            result += "[" + self.args + "]"
        result += "\n"
        result += self.formula
        result += "\n\\end{tikzpicture}"

    def __str__(self):
        """Generate textual representation."""
        return "TikzPicture(" + self.args + "; " + repr(self.formula) + ")"

    def visit(self, visitor, *args, **kw):
        """Process with TreeVisitor object. Passes ``args`` and ``kw`` to the corresponding method of ``visitor``."""
        return visitor.process_tikz_picture(self, *args, **kw)


class PSTricksPicture(Formula):
    """Represents a PSTricks picture."""

    def __init__(self, formula, args):
        """Initialize object."""
        super(PSTricksPicture, self).__init__(formula)
        self.args = args
        assert isinstance(self.args, dict)

    def recombine_as_text(self, reescape=True):
        """Recombine subtree as LaTeX source text."""
        result = "\\begin{pstricks}{" + self.args + "}\n"
        result += self.formula
        result += "\n\\end{pstricks}"

    def __str__(self):
        """Generate textual representation."""
        return "PSTricksPicture(" + self.args + "; " + repr(self.formula) + ")"

    def visit(self, visitor, *args, **kw):
        """Process with TreeVisitor object. Passes ``args`` and ``kw`` to the corresponding method of ``visitor``."""
        return visitor.process_pstricks_picture(self, *args, **kw)


class Word(Base):
    """Represents a word."""

    def __init__(self):
        """Initialize object."""
        self.parts = list()

    def recombine_as_text(self, reescape=True):
        """Recombine subtree as LaTeX source text."""
        if len(self.parts) == 0:
            return " "
        else:
            result = ""
            for part in self.parts:
                if isinstance(part, Words):
                    result += "{" + part.recombine_as_text(reescape) + "}"
                else:
                    result += part.recombine_as_text(reescape)
            return result

    def __str__(self):
        """Generate textual representation."""
        return "Word(" + str(self.parts) + ")"

    def visit(self, visitor, *args, **kw):
        """Process with TreeVisitor object. Passes ``args`` and ``kw`` to the corresponding method of ``visitor``."""
        return visitor.process_word(self, *args, **kw)


class Link(Base):
    """Represents a link."""

    def __init__(self, destination, link_text=None):
        """Initialize object."""
        self.destination = destination
        self.text = link_text

    def recombine_as_text(self, reescape=True):
        """Recombine subtree as LaTeX source text."""
        if self.text is None:
            return "\\url{" + self.destination + "}"
        else:
            return "\\href{" + self.destination + "}{" + self.text.recombine_as_text(reescape) + "}"

    def __str__(self):
        """Generate textual representation."""
        if self.text is None:
            return "URL{" + str(self.destination) + "}"
        else:
            return "Link{" + str(self.destination) + "}(" + str(self.text) + ")"

    def print(self, indent):
        """Print to stdout with given indentation."""
        print("  " * indent + str(self))

    def visit(self, visitor, *args, **kw):
        """Process with TreeVisitor object. Passes ``args`` and ``kw`` to the corresponding method of ``visitor``."""
        return visitor.process_link(self, *args, **kw)


class Reference(Base):
    """Represents a reference."""

    def __init__(self, destination, text=None):
        """Initialize object."""
        self.destination = destination
        self.text = text

    def recombine_as_text(self, reescape=True):
        """Recombine subtree as LaTeX source text."""
        if self.text is None:
            text = ""
        else:
            text = "[" + self.text.recombine_as_text(reescape) + "]"
        return "\\href" + text + "{" + self.destination + "}"

    def __str__(self):
        """Generate textual representation."""
        return "Reference{" + self.destination + "}(" + str(self.text) + ")"

    def print(self, indent):
        """Print to stdout with given indentation."""
        print("  " * indent + str(self))

    def visit(self, visitor, *args, **kw):
        """Process with TreeVisitor object. Passes ``args`` and ``kw`` to the corresponding method of ``visitor``."""
        return visitor.process_reference(self, *args, **kw)


class Words(Base):
    """Represents a collection of words."""

    def __init__(self):
        """Initialize object."""
        self.formatting = None
        self.words = list()

    def recombine_as_text(self, reescape=True):
        """Recombine subtree as LaTeX source text."""
        result = ""
        first = True
        for word in self.words:
            if first:
                first = False
            else:
                result += " "
            result += word.recombine_as_text(reescape)
        if self.formatting is not None:
            if self.formatting == "emphasize":
                result = "\\emph{" + result + "}"
            elif self.formatting == "strong":
                result = "\\textbf{" + result + "}"
        return result

    def __str__(self):
        """Generate textual representation."""
        formString = ""
        if self.formatting is not None:
            formString = "<" + self.formatting + ">"
        return "Words" + formString + "(" + str(self.words) + ")"

    def print(self, indent):
        """Print to stdout with given indentation."""
        print("  " * indent + str(self))

    def visit(self, visitor, *args, **kw):
        """Process with TreeVisitor object. Passes ``args`` and ``kw`` to the corresponding method of ``visitor``."""
        return visitor.process_words(self, *args, **kw)


class DisplayFormula(Formula):
    """Represents a display-style formula."""

    def __str__(self):
        """Generate textual representation."""
        return "DisplayFormula(" + self.formula + ")"

    def visit(self, visitor, *args, **kw):
        """Process with TreeVisitor object. Passes ``args`` and ``kw`` to the corresponding method of ``visitor``."""
        return visitor.process_display_formula(self, *args, **kw)


class AlignFormula(Formula):
    """Represents a align-style formula."""

    def __str__(self):
        """Generate textual representation."""
        return "AlignFormula(" + self.formula + ")"

    def visit(self, visitor, *args, **kw):
        """Process with TreeVisitor object. Passes ``args`` and ``kw`` to the corresponding method of ``visitor``."""
        return visitor.process_align_formula(self, *args, **kw)


class CodeBlock(Code):
    """Represents a code block."""

    def __str__(self):
        """Generate textual representation."""
        return "CodeBlock('" + self.type + "', '" + self.code + "')"

    def print(self, indent):
        """Print to stdout with given indentation."""
        print("  " * indent + "CodeBlock<" + self.type + ">:")
        for line in self.code.split("\n"):
            print("  " * (indent + 1) + "|" + line + "|")

    def visit(self, visitor, *args, **kw):
        """Process with TreeVisitor object. Passes ``args`` and ``kw`` to the corresponding method of ``visitor``."""
        return visitor.process_code_block(self, *args, **kw)


class Block(Base):
    """Represents a block."""

    def __init__(self, *elements):
        """Initialize object."""
        self.elements = list(elements)
        self.labels = []

    def get_name(self):
        """Return name of block."""
        return "Block"

    def __str__(self):
        """Generate textual representation."""
        return self.get_name() + "(" + str(self.elements) + ")"

    def print(self, indent):
        """Print to stdout with given indentation."""
        print("  " * indent + self.get_name() + ":")
        for elt in self.elements:
            elt.print(indent + 1)
        if len(self.elements) == 0:
            print("  " * (indent + 1) + "(nothing)")

    def visit(self, visitor, *args, **kw):
        """Process with TreeVisitor object. Passes ``args`` and ``kw`` to the corresponding method of ``visitor``."""
        return visitor.process_block(self, *args, **kw)


class SpecialBlock(Block):
    """Represents a special block."""

    def __init__(self, type):
        """Initialize object."""
        super(SpecialBlock, self).__init__()
        self.type = type

    def get_name(self):
        """Return name of block."""
        return "SpecialBlock<" + self.type + ">"

    def visit(self, visitor, *args, **kw):
        """Process with TreeVisitor object. Passes ``args`` and ``kw`` to the corresponding method of ``visitor``."""
        return visitor.process_special_block(self, *args, **kw)


class Enumeration(Block):
    """Represents an enumeration or itemize."""

    def __init__(self, type):
        """Initialize object.

        ``type`` must be "ul" for an unsorted list or "ol" for an enumeration.
        """
        super(Enumeration, self).__init__()
        self.type = type

    def get_name(self):
        """Return name of block."""
        return "Enumeration<" + self.type + ">"

    def visit(self, visitor, *args, **kw):
        """Process with TreeVisitor object. Passes ``args`` and ``kw`` to the corresponding method of ``visitor``."""
        return visitor.process_enumeration(self, *args, **kw)


class TheoremEnvironment(Block):
    """Represents a theorem environment."""

    def __init__(self, type):
        """Initialize object."""
        super(TheoremEnvironment, self).__init__()
        self.optional_title = None
        self.type = type  # definition, lemma, theorem
        if self.type == 'proof':
            self.qed = True
        else:
            self.qed = False

    def get_name(self):
        """Return name of block."""
        res = "TheoremEnvironment<" + self.type
        if self.qed:
            res += "; qed"
        res += ">[" + str(self.optional_title) + "]"
        return res

    def visit(self, visitor, *args, **kw):
        """Process with TreeVisitor object. Passes ``args`` and ``kw`` to the corresponding method of ``visitor``."""
        return visitor.process_theorem_environment(self, *args, **kw)


class TitledBlock(Block):
    """Represents a titled block."""

    def __init__(self, title):
        """Initialize object."""
        super(TitledBlock, self).__init__()
        self.title = title

    def get_name(self):
        """Return name of block."""
        return "TitledBlock"

    def __str__(self):
        """Generate textual representation."""
        return self.get_name() + "(" + str(self.title) + ":" + str(self.elements) + ")"

    def print(self, indent):
        """Print to stdout with given indentation."""
        print("  " * indent + self.get_name() + ":")
        print("  " * (indent + 1) + "Title:")
        self.title.print(indent + 2)
        print("  " * (indent + 1) + "Content:")
        for elt in self.elements:
            elt.print(indent + 2)
        if len(self.elements) == 0:
            print("  " * (indent + 2) + "(nothing)")

    def visit(self, visitor, *args, **kw):
        """Process with TreeVisitor object. Passes ``args`` and ``kw`` to the corresponding method of ``visitor``."""
        return visitor.process_titled_block_other(self, *args, **kw)


class Chapter(TitledBlock):
    """Represents a chapter."""

    def get_name(self):
        """Return name of block."""
        return "Chapter"

    def visit(self, visitor, *args, **kw):
        """Process with TreeVisitor object. Passes ``args`` and ``kw`` to the corresponding method of ``visitor``."""
        return visitor.process_titled_block_chapter(self, *args, **kw)


class Section(TitledBlock):
    """Represents a section."""

    def get_name(self):
        """Return name of block."""
        return "Section"

    def visit(self, visitor, *args, **kw):
        """Process with TreeVisitor object. Passes ``args`` and ``kw`` to the corresponding method of ``visitor``."""
        return visitor.process_titled_block_section(self, *args, **kw)


class SubSection(TitledBlock):
    """Represents a subsection."""

    def get_name(self):
        """Return name of block."""
        return "SubSection"

    def visit(self, visitor, *args, **kw):
        """Process with TreeVisitor object. Passes ``args`` and ``kw`` to the corresponding method of ``visitor``."""
        return visitor.process_titled_block_subsection(self, *args, **kw)


class SubSubSection(TitledBlock):
    """Represents a subsubsection."""

    def get_name(self):
        """Return name of block."""
        return "SubSubSection"

    def visit(self, visitor, *args, **kw):
        """Process with TreeVisitor object. Passes ``args`` and ``kw`` to the corresponding method of ``visitor``."""
        return visitor.process_titled_block_subsubsection(self, *args, **kw)


class PictureGroup(Base):
    """Represents a group of pictures."""

    def __init__(self):
        """Initialize object."""
        self.pictures = []

    def recombine_as_text(self, reescape=True):
        """Recombine subtree as LaTeX source text."""
        result = r'\begin{picturegroup}'
        for picture in self.pictures:
            result += r'\picture{{{0}}}{{{1}}}'.format(picture[0].recombine_as_text(reescape), picture[1].recombine_as_text(reescape))
        result += r'\end{picturegroup}'
        return result

    def __str__(self):
        """Generate textual representation."""
        return "PictureGroup(" + ", ".join(["Picture({0}: {1})".format(picture[0], picture[1]) for picture in self.pictures]) + ")"

    def visit(self, visitor, *args, **kw):
        """Process with TreeVisitor object. Passes ``args`` and ``kw`` to the corresponding method of ``visitor``."""
        return visitor.process_picture_group(self, *args, **kw)


class FormulaList(Base):
    """Represents a list of formulae."""

    def __init__(self):
        """Initialize object."""
        self.formulae = []

    def recombine_as_text(self, reescape=True):
        """Recombine subtree as LaTeX source text."""
        result = r'\begin{formulalist}'
        for formula in self.formulae:
            result += r'\formula{{{0}}}'.format(formula)
        result += r'\end{formulalist}'
        return result

    def __str__(self):
        """Generate textual representation."""
        return "FormulaList(" + ", ".join(["Formula({0})".format(formula) for formula in self.formulae]) + ")"

    def visit(self, visitor, *args, **kw):
        """Process with TreeVisitor object. Passes ``args`` and ``kw`` to the corresponding method of ``visitor``."""
        return visitor.process_formula_list(self, *args, **kw)


class TreeVisitor(object):
    """Allows efficient processing of a LaTeX tree."""

    def process_word_part(self, word_part, *args, **kw):
        """Process a WordPart object."""
        raise NotImplementedError()

    def process_word(self, word, *args, **kw):
        """Process a Word object."""
        raise NotImplementedError()

    def process_words(self, words, *args, **kw):
        """Process a Words object."""
        raise NotImplementedError()

    def process_comment(self, comment, *args, **kw):
        """Process a Comment object."""
        raise NotImplementedError()

    def process_tabular(self, tabular, *args, **kw):
        """Process a Tabular object."""
        raise NotImplementedError()

    def process_include_graphics(self, gfx, *args, **kw):
        """Process a IncludeGraphics object."""
        raise NotImplementedError()

    def process_link(self, link, *args, **kw):
        """Process a Link object."""
        raise NotImplementedError()

    def process_reference(self, ref, *args, **kw):
        """Process a Reference object."""
        raise NotImplementedError()

    def process_tikz_picture(self, tikz_picture, *args, **kw):
        """Process a TikzPicture object."""
        raise NotImplementedError()

    def process_pstricks_picture(self, pstricks_picture, *args, **kw):
        """Process a PSTricksPicture object."""
        raise NotImplementedError()

    def process_display_formula(self, formula, *args, **kw):
        """Process a DisplayFormula object."""
        raise NotImplementedError()

    def process_align_formula(self, formula, *args, **kw):
        """Process a AlignFormula object."""
        raise NotImplementedError()

    def process_inline_formula(self, formula, *args, **kw):
        """Process a Formula object."""
        raise NotImplementedError()

    def process_titled_block_chapter(self, chapter, *args, **kw):
        """Process a Chapter object."""
        raise NotImplementedError()

    def process_titled_block_section(self, section, *args, **kw):
        """Process a Section object."""
        raise NotImplementedError()

    def process_titled_block_subsection(self, subsection, *args, **kw):
        """Process a SubSection object."""
        raise NotImplementedError()

    def process_titled_block_subsubsection(self, subsubsection, *args, **kw):
        """Process a SubSubSection object."""
        raise NotImplementedError()

    def process_titled_block_other(self, titled_block, *args, **kw):
        """Process a TitledBlock object."""
        raise NotImplementedError()

    def process_theorem_environment(self, theorem_env, *args, **kw):
        """Process a TheoremEnvironment object."""
        raise NotImplementedError()

    def process_enumeration(self, enumeration, *args, **kw):
        """Process an Enumeration object."""
        raise NotImplementedError()

    def process_special_block(self, special_block, *args, **kw):
        """Process a SpecialBlock object."""
        raise NotImplementedError()

    def process_block(self, block, *args, **kw):
        """Process a Block object."""
        raise NotImplementedError()

    def process_code_block(self, code, *args, **kw):
        """Process a CodeBlock object."""
        raise NotImplementedError()

    def process_code_inline(self, code, *args, **kw):
        """Process a Code object."""
        raise NotImplementedError()

    def process_picture_group(self, picture_group, *args, **kw):
        """Process a PictureGroup object."""
        raise NotImplementedError()

    def process_formula_list(self, formula_list, *args, **kw):
        """Process a FormulaList object."""
        raise NotImplementedError()

    def process_language(self, language, *args, **kw):
        """Process a Language object."""
        raise NotImplementedError()
