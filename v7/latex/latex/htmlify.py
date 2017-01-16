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

"""Convert LaTeX trees to HTML code."""

from __future__ import unicode_literals

from . import tree

import pygments
import pygments.lexers
import pygments.formatters
import re
import urllib.parse
import nikola.utils

LOGGER = nikola.utils.get_logger('compile_latex.htmlify', nikola.utils.STDERR_HANDLER)


def _escape_html(text, escape_spaces=False):
    """Escape a string to be usable in HTML code."""
    result = ""
    for c in text:
        if c == "<":
            result += "&lt;"
        elif c == ">":
            result += "&gt;"
        elif c == "&":
            result += "&amp;"
        elif c == '"':
            result += "&quot;"
        elif c == "'":
            result += "&#39;"
        elif c == " " and escape_spaces:
            result += "&nbsp;"
        elif ord(c) < 32 or 127 <= ord(c) < 160:
            result += '&#x{0};'.format(hex(ord(c))[2:])
        else:
            result += c
    return result


def _escape_html_argument(text):
    """Escape a string to be usable as an HTML tag argument."""
    result = ""
    for c in text:
        if c == "<":
            result += "&lt;"
        elif c == ">":
            result += "&gt;"
        elif c == "&":
            result += "&amp;"
        elif c == '"':
            result += "&quot;"
        elif c == "'":
            result += "&#39;"
        elif c == " ":
            result += " "
        elif '0' <= c <= '9' or 'A' <= c <= 'Z' or 'a' <= c <= 'z' or c in {'/', ':', '.', '@', '-', '_'}:
            result += c
        else:
            result += '&#x{0};'.format(hex(ord(c))[2:])
    return result


def _escape_url(text):
    """Escape a URL with percent encoding."""
    return urllib.parse.quote(text, safe=':/#').replace(' ', '%20')


class HTMLifyContext:
    """Encapsulates formula context and some HTMLifying options and state."""

    def __init__(self, formula_context, beautify=False):
        """Initialize HTMLify context."""
        self.formula_context = formula_context
        self.beautify = beautify
        self.item_level = 0
        self.enum_level = 0

    def clone(self, beautify=None):
        """Create a clone with beautification set to a specific value."""
        result = HTMLifyContext(self.formula_context.clone(), beautify=self.beautify if beautify is None else beautify)
        result.item_level = self.item_level
        result.enum_level = self.enum_level
        return result


class HTMLifyException(Exception):
    """Raised when errors appear during HTMLification."""

    pass


class HTMLifyVisitor(tree.TreeVisitor):
    """Visits all nodes of the LaTeX tree to generate HTML code."""

    def __init__(self, htmlify_context, formula_renderer, latex_context):
        """Initialize visitor."""
        self.htmlify_context = htmlify_context
        self.latex_context = latex_context
        self.formula_renderer = formula_renderer

    def __get_non_beautifying_visitor(self):
        """Return an instance which doesn't beautify. Might be ``self``."""
        if self.htmlify_context.beautify:
            return HTMLifyVisitor(self.htmlify_context.clone(beautify=False), self.formula_renderer, self.latex_context)
        else:
            return self

    def __add_indent(self, text, indent):
        """Add indentation if beautification is turned on."""
        if self.htmlify_context.beautify:
            return (" " * indent) + text + "\n"
        else:
            return text

    def __add_block(self, block_type, css_class, content, indent, **kw):
        """Add content into a HTML block.

        ``block_type`` is the block tag type;
        ``css_class`` is the CSS class(es) added to the block tag;
        ``content`` is the content inside the block;
        ``indent`` is the indent to use for the block tags;
        ``kw`` allows to set further arguments to the block tag.
        """
        arguments = []
        if css_class is not None:
            arguments.append(" class='{0}'".format(_escape_html_argument(css_class)))
        for key, value in sorted(kw.items()):
            arguments.append(" {0}='{1}'".format(key, _escape_html_argument(value)))
        return ''.join([
            self.__add_indent("<{0}{1}>".format(block_type, ''.join(arguments)), indent),
            content,
            self.__add_indent("</{0}>".format(block_type), indent),
        ])

    def process_word_part(self, word_part, indent):
        """Process a WordPart object."""
        if word_part.text == " ":
            return "&nbsp;"
        else:
            return _escape_html(word_part.text)

    def process_word(self, word, indent):
        """Process a Word object."""
        result = [part.visit(self, indent) for part in word.parts]
        return "".join(result)

    def process_words(self, words, indent):
        """Process a Words object."""
        result = []
        first = True
        for word in words.words:
            if first:
                first = False
            else:
                result.append(" ")
            result.append(word.visit(self, indent))
        result = ''.join(result)
        if words.formatting is not None:
            if words.formatting == "emphasize":
                tag = 'em'
            elif words.formatting == "strong":
                tag = 'strong'
            elif words.formatting == "italics":
                tag = 'i'
            elif words.formatting == "teletype":
                tag = 'tt'
            else:
                raise HTMLifyException("Unknown formatting style '{0}'!".format(words.formatting))
            result = "<{0}>{1}</{0}>".format(tag, result)
        return result

    def process_comment(self, comment, indent):
        """Process a Comment object."""
        return ""

    def process_tabular(self, tabular, indent):
        """Process a Tabular object."""
        def find_cell_borders(r, c):
            """Find cell border information."""
            def has_line(lines_data, column):
                for line in lines_data:
                    if line is None:
                        return True
                    elif (line[0] is None or line[0] <= c + 1) and (line[1] is None or c + 1 <= line[1]):
                        return True
                return False

            # Find left borders
            b_left = tabular.alignment[c].left_border
            if c > 0:
                b_left |= tabular.alignment[c - 1].right_border
            # Find right borders
            if c == len(tabular.alignment) - 1:
                b_right = tabular.alignment[c].right_border
            else:
                b_right = False
            # Find top borders
            b_top = has_line(tabular.lines_data[r], c)
            # Find bottom borders
            b_bottom = False
            if r == len(tabular.rows) - 1 and len(tabular.lines_data) + 1 > r:
                b_bottom = has_line(tabular.lines_data[r + 1], c)
            return b_left, b_right, b_top, b_bottom

        def get_border_class(b_left, b_right, b_top, b_bottom):
            """Obtain CSS class describing borders for cell."""
            clazz = ""
            if b_left:
                clazz += "l"
            if b_right:
                clazz += "r"
            if b_top:
                clazz += "t"
            if b_bottom:
                clazz += "b"
            return " class='cell-{}'".format(clazz) if clazz else ""

        def get_alignment(c):
            """Obtain CSS style describing cell alignment."""
            align = tabular.alignment[c].align
            if align == tree.TabularAlignEnum.Left:
                return ' style="text-align: left;"'
            elif align == tree.TabularAlignEnum.Center:
                return ' style="text-align: center;"'
            elif align == tree.TabularAlignEnum.Right:
                return ' style="text-align: right;"'
            return ''

        content = []
        for r, row in enumerate(tabular.rows):
            row_content = []
            for c in range(len(tabular.alignment)):
                b_left, b_right, b_top, b_bottom = find_cell_borders(r, c)
                cell_content = row[c].visit(self, indent + 4) if c < len(row) else ''
                cell = "<td{0}{1}>{2}</td>".format(get_border_class(b_left, b_right, b_top, b_bottom), get_alignment(c), cell_content)
                row_content.append(self.__add_indent(cell, indent + 3))
            content.append(self.__add_block("tr", None, ''.join(row_content), indent + 2))
        return self.__add_block("div", "tabular-wrapper", self.__add_block("table", None, ''.join(content), indent + 1), indent)

    @staticmethod
    def __convert_distance_unit(unit, horizontal):
        """Convert a LaTeX distance unit into a CSS distance unit."""
        if unit.endswith(r'\textwidth') and horizontal:
            unit = unit[:-len(r'\textwidth')]
            if len(unit) > 0:
                return "{0:.2f}%".format(float(unit) * 100)
            else:
                return "100%"
        if unit.endswith(r'\textheight') and not horizontal:
            unit = unit[:-len(r'\textheight')]
            if len(unit) > 0:
                return "{0:.2f}%".format(float(unit) * 100)
            else:
                return "100%"
        elif unit.endswith('cm'):
            return "{0}em".format(float(unit[:-len('cm')]) * 20)
        else:
            return "{0}px".format(float(unit))

    def process_include_graphics(self, gfx, indent, extract_size=False):
        """Process a IncludeGraphics object."""
        result = ["<img src='{0}' class='include-graphics'".format(_escape_url(gfx.url))]
        alt = ""
        kw = {}
        if len(gfx.args) > 0:
            if 'width' in gfx.args:
                kw["width"] = self.__convert_distance_unit(gfx.args['width'], True)
            if 'height' in gfx.args:
                kw["height"] = self.__convert_distance_unit(gfx.args['height'], True)
            if not extract_size:
                for key, value in kw.items():
                    result.append(" {}='{}'".format(key, value))
            if 'alt' in gfx.args:
                alt = gfx.args['alt']
        result.append(" alt='" + _escape_html_argument(alt) + "'/>")
        result = ''.join(result)
        return (result, kw) if extract_size else result

    def process_link(self, link, indent):
        """Process a Link object."""
        if link.text is None:
            content = '<tt class="{0}">{1}</tt>'.format('url-as-text', _escape_html(link.destination))
        else:
            content = link.text.visit(self, 0)
        return "<a href='{0}'>{1}</a>".format(_escape_url(link.destination), content)

    def process_reference(self, ref, indent):
        """Process a Reference object."""
        url, text = self.latex_context.provide_link(ref.destination)
        if ref.text is None:
            text = _escape_html(text)
        else:
            text = ref.text.visit(self, 0)
        result = "<a href='{0}'>{1}</a>".format(_escape_url(url), text)
        return result

    def __process_formula(self, the_formula, formula_type):
        """Render the given formula."""
        return self.formula_renderer.render(the_formula.formula, self.htmlify_context.formula_context, formula_type, self.latex_context)

    def process_tikz_picture(self, tikz_picture, indent):
        """Process a TikzPicture object."""
        return '<span class="tikz-formula">{}</span>'.format(self.__process_formula(tikz_picture, ("tikzpicture", tikz_picture.args)))

    def process_pstricks_picture(self, pstricks, indent):
        """Process a PSTricksPicture object."""
        return '<span class="pstricks-formula">{}</span>'.format(self.__process_formula(pstricks, ("pstricks", pstricks.args)))

    def process_display_formula(self, formula, indent):
        """Process a DisplayFormula object."""
        return self.__add_block("div", "display-formula", self.__add_indent(self.__process_formula(formula, "display"), indent + 1), indent)

    def process_align_formula(self, formula, indent):
        """Process a AlignFormula object."""
        return self.__add_block("div", "align-formula", self.__add_indent(self.__process_formula(formula, "align"), indent + 1), indent)

    def process_inline_formula(self, formula, indent):
        """Process a Formula object."""
        return '<span class="inline-formula">{0}</span>'.format(self.__process_formula(formula, "inline"))

    def process_titled_block_chapter(self, block, indent):
        """Process a Chapter object."""
        header_type = "h1"
        header_class = None
        css_class = "chapter-block"
        header = self.__add_block(header_type, header_class, self.__add_indent(block.title.visit(self.__get_non_beautifying_visitor(), 0).strip(), indent + 2), indent + 1)
        return self.__add_block("div", css_class, header + self.process_block(block, indent + 1), indent)

    def process_titled_block_section(self, block, indent):
        """Process a Section object."""
        header_type = "h2"
        header_class = None
        css_class = "section-block"
        header = self.__add_block(header_type, header_class, self.__add_indent(block.title.visit(self.__get_non_beautifying_visitor(), 0).strip(), indent + 2), indent + 1)
        return self.__add_block("div", css_class, header + self.process_block(block, indent + 1), indent)

    def process_titled_block_subsection(self, block, indent):
        """Process a SubSection object."""
        header_type = "h3"
        header_class = None
        css_class = "subsection-block"
        header = self.__add_block(header_type, header_class, self.__add_indent(block.title.visit(self.__get_non_beautifying_visitor(), 0).strip(), indent + 2), indent + 1)
        return self.__add_block("div", css_class, header + self.process_block(block, indent + 1), indent)

    def process_titled_block_subsubsection(self, block, indent):
        """Process a SubSubSection object."""
        header_type = "h4"
        header_class = None
        css_class = "subsubsection-block"
        header = self.__add_block(header_type, header_class, self.__add_indent(block.title.visit(self.__get_non_beautifying_visitor(), 0).strip(), indent + 2), indent + 1)
        return self.__add_block("div", css_class, header + self.process_block(block, indent + 1), indent)

    def process_titled_block_other(self, block, indent):
        """Process a TitledBlock object."""
        raise HTMLifyException("Unknown titled block type '{0}'!".format(type(block)))

    def __get_theorem_environment_name(self, type):
        """Retrieve title for a theorem environment of type ``type``."""
        if type == "definition":
            return self.latex_context.thm_names['def_name']
        elif type == "definitions":
            return self.latex_context.thm_names['defs_name']
        elif type == "lemma":
            return self.latex_context.thm_names['lemma_name']
        elif type == "proposition":
            return self.latex_context.thm_names['prop_name']
        elif type == "theorem":
            return self.latex_context.thm_names['thm_name']
        elif type == "corollary":
            return self.latex_context.thm_names['cor_name']
        elif type == "example":
            return self.latex_context.thm_names['example_name']
        elif type == "examples":
            return self.latex_context.thm_names['examples_name']
        elif type == "remark":
            return self.latex_context.thm_names['remark_name']
        elif type == "remarks":
            return self.latex_context.thm_names['remarks_name']
        elif type == "proof":
            return self.latex_context.thm_names['proof_name']
        else:
            raise HTMLifyException("Unknown theorem environment name '{0}'!".format(type))

    def process_theorem_environment(self, block, indent):
        """Process a TheoremEnvironment object."""
        title = self.__get_theorem_environment_name(block.type)
        if block.optional_title is not None:
            title += ' ({0})'.format(block.optional_title.visit(self.__get_non_beautifying_visitor(), 0).strip())
        title += "."
        css = "theorem-environment theorem-{0}-environment".format(block.type)
        labels = []
        for label in block.labels:
            labels.append(self.__add_indent("<a name='" + _escape_html_argument(label) + "'></a>", indent + 2))
        header = self.__add_block("div", "theorem-header theorem-{0}-header".format(block.type), ''.join(labels) + self.__add_indent(title, indent + 2), indent + 1)
        content = self.process_block(block, indent + 1, False, "theorem-content theorem-{0}-content".format(block.type))
        qed = ''
        if block.qed:
            qed = self.__add_indent('<div class="qed-block"><span class="qed-sign"></span></div>', indent + 1)
            css += " qed"
        return self.__add_block("div", css, header + content + qed, indent)

    def __process_block_content(self, block, indent):
        """Helper function to process content of a block. This ensures that Words objects are encapsulated in <p>."""
        result = []
        for elt in block.elements:
            if isinstance(elt, tree.Words):
                result.append(self.__add_block("p", None, self.__add_indent(elt.visit(self.__get_non_beautifying_visitor(), 0).strip(), indent + 1), indent))
            else:
                result.append(elt.visit(self, indent))
        return ''.join(result)

    def process_enumeration(self, block, indent):
        """Process an Enumeration object."""
        content = []
        css_class = None
        for label in block.labels:
            content.append(self.__add_indent("<a name='{0}'></a>".format(_escape_html_argument(label)), indent + 1))
        if block.type == "ul":
            self.htmlify_context.item_level += 1
            css_class = "item-level-{0}".format(str(self.htmlify_context.item_level))
        else:
            self.htmlify_context.enum_level += 1
            css_class = "enum-level-{0}".format(str(self.htmlify_context.enum_level))
        for elt in block.elements:
            # Get labels for element
            labels = []
            if isinstance(elt, tree.Block):
                labels = elt.labels
            # Get rid of block containing only words or a formula object
            if isinstance(elt, tree.Block) and len(elt.elements) == 1 and isinstance(elt.elements[0], (tree.Words, tree.Formula)):
                elt = elt.elements[0]
            # Now generate output
            labels_tags = []
            for label in labels:
                labels_tags.append("<a name='{0}'></a>".format(_escape_html_argument(label)))
            if isinstance(elt, tree.Block) and len(elt.elements) == 0:
                content.append(self.__add_indent("<li>{0}</li>".format(''.join(labels_tags)), indent + 1))
            elif isinstance(elt, tree.Words):
                content.append(self.__add_indent("<li>{0}{1}</li>".format(''.join(labels_tags), elt.visit(self.__get_non_beautifying_visitor(), 0).strip()), indent + 1))
            else:
                labels_tags = [self.__add_indent(label_tag, indent + 2) for label_tag in labels_tags]
                if isinstance(elt, tree.Block):
                    block_content = self.__process_block_content(elt, indent + 2)
                else:
                    block_content = elt.visit(self, indent + 2)
                content.append(self.__add_block("li", None, ''.join(labels_tags) + block_content, indent + 1))
        if block.type == "ul":
            self.htmlify_context.item_level -= 1
        else:
            self.htmlify_context.enum_level -= 1
        return self.__add_block(block.type, css_class, ''.join(content), indent)

    def process_block(self, block, indent, add_labels=True, css_classes=None, container_type='div'):
        """Process a Block object."""
        labels = []
        if add_labels:
            for label in block.labels:
                labels.append(self.__add_indent("<a name='{0}'></a>".format(_escape_html_argument(label)), indent + 1))
        return self.__add_block(container_type, css_classes, ''.join(labels) + self.__process_block_content(block, indent + 1), indent)

    def process_special_block(self, block, indent):
        """Process a SpecialBlock object."""
        if block.type == 'blockquote':
            css_class = 'block-quote'
            container_type = 'blockquote'
        elif block.type == 'center':
            css_class = 'center-block'
            container_type = 'div'
        else:
            raise HTMLifyException("Unknown special block type '{0}'!".format(block.type))
        return self.process_block(block, indent, True, css_class, container_type)

    # The following regular expression and its applications are taken from plugins/task/listings.py of an older version of Nikola; Copyright © 2012-2016 Roberto Alsina and others
    __CODERE = re.compile('<div class="(?:highlight|code|codehilite)"><pre>(.*?)</pre></div>', flags=re.MULTILINE | re.DOTALL)

    def process_code_block(self, code, indent):
        """Process a CodeBlock object."""
        content = pygments.highlight(code.code, pygments.lexers.get_lexer_by_name(code.type), pygments.formatters.HtmlFormatter(css_class='code', linenos='inline', nowrap=False, anchorlinenos=False))
        content = self.__CODERE.sub(r'<pre class="code literal-block">\1</pre>', content)
        return "<div class='code-{0}'>{1}</div>".format(code.type, content)

    def process_code_inline(self, code, indent):
        """Process a Code object."""
        content = pygments.highlight(code.code, pygments.lexers.get_lexer_by_name(code.type), pygments.formatters.HtmlFormatter(css_class='code', linenos=False, nowrap=False, anchorlinenos=False))
        content = self.__CODERE.sub(r'<code class="code literal-block">\1</code>', content).replace("\n", "")
        return "<span class='code-{0} inline-code'>{1}</span>".format(code.type, content)

    @staticmethod
    def __extract_singleton(root):
        """Return the single element if there is one, or None if there is none."""
        if isinstance(root, tree.Words):
            singleton = None
            for word in root.words:
                s = HTMLifyVisitor.__extract_singleton(word)
                if s is not None:
                    if singleton is not None:
                        return None
                    singleton = s
            return singleton
        elif isinstance(root, tree.Word):
            singleton = None
            for part in root.parts:
                s = HTMLifyVisitor.__extract_singleton(part)
                if s is not None:
                    if singleton is not None:
                        return None
                    singleton = s
            return singleton
        else:
            return root

    def process_picture_group(self, picturegroup, indent):
        """Process a PictureGroup object."""
        content = ""
        for picture in picturegroup.pictures:
            singleton = HTMLifyVisitor.__extract_singleton(picture[1])
            if singleton is not None and isinstance(singleton, tree.IncludeGraphics):
                pc, kw = self.process_include_graphics(singleton, indent + 3, extract_size=True)
                if len(kw) > 0:
                    kw = {"style": " ".join(["{0}: {1};".format(k, v) for k, v in sorted(kw.items())])}
            else:
                pc = picture[1].visit(self, indent + 3)
                kw = {}
            picture_content = self.__add_block("div", "content", pc, indent + 2)
            picture_content += self.__add_block("div", "title", picture[0].visit(self, indent + 3), indent + 2)
            content += self.__add_block("div", "picture", picture_content, indent + 1, **kw)
        return self.__add_block("div", "picture-group", content, indent)

    def process_formula_list(self, formulalist, indent):
        """Process a FormulaList object."""
        content = []
        for formula in formulalist.formulae:
            content.append(self.__add_block("div", "formula", formula.visit(self, indent + 2), indent + 1))
        return self.__add_block("div", "formula-list", ''.join(content), indent)

    def process_language(self, language, indent):
        """Process a Language object."""
        return self.__add_block("span" if language.inline else "div", None, language.element.visit(self, indent + 1), indent, lang=language.locale)


def HTMLify(root, formula_renderer, latex_context, beautify=False, outer_indent=0):
    """Convert LaTeX tree ``root`` to HTML.

    ``formula_renderer`` must be a formula rendering plugin;
    ``latex_context`` must be a LaTeX context object;
    ``beautify`` can be set to ``True`` to beautify generated HTML code;
    ``outer_indent`` can be set to a positive value to indent the generated HTML code if it is beautified.
    """
    htmlify_context = HTMLifyContext(formula_renderer.create_context(), beautify=beautify)
    htmlify_visitor = HTMLifyVisitor(htmlify_context, formula_renderer, latex_context)
    return root.visit(htmlify_visitor, outer_indent)
