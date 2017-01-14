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

"""Render formulas for LaTeX post compiler as images using the latex_formula_renderer plugin."""

from __future__ import unicode_literals

import nikola.plugin_categories
import nikola.utils

import json
import os.path
import sys

LOGGER = nikola.utils.get_logger('compile_latex.formula.image', nikola.utils.STDERR_HANDLER)


class FormulaContext(object):
    """Stores information about the formula renderer.

    For the formula image renderer, scale and color are stored in the context.
    """

    def __init__(self, scale, color):
        """Create formula context with given scale and color."""
        self.scale = scale
        self.color = color

    def clone(self):
        """Clone this FormulaContext object."""
        return FormulaContext(self.scale, self.color)


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


class LatexImageFormulaRenderer(nikola.plugin_categories.CompilerExtension):
    """Render LaTeX formulae as image files using the latex_formula_renderer plugin."""

    name = 'latex_formula_image_renderer'
    compiler_name = 'latex'
    latex_plugin_type = 'formula_renderer'

    def __init__(self):
        """Initialize plugin."""
        super(LatexImageFormulaRenderer, self).__init__()
        self.__formula_scale = 1.25
        self.__formula_color = (0., 0., 0.)

    def _get_formulae_filename(self, post, lang):
        """Get filename for post and language to store LaTeX formulae in."""
        return post.translated_base_path(lang) + '.ltxfor'

    def _collect_formulas(self):
        """Collect LaTeX formulae used in posts."""
        # Look for candidates from posts
        candidates = set()
        for post in self.site.timeline:
            if post.compiler.name != 'latex':
                continue
            for lang in self.site.config['TRANSLATIONS']:
                candidates.add(self._get_formulae_filename(post, lang))
        # Look for candidates from extra formula sources
        for dirpath, _, filenames in os.walk(self.__extra_formula_sources, followlinks=True):
            for filename in filenames:
                if filename.endswith('.texfor'):
                    candidates.add(os.path.join(dirpath, filename))
        # Check the candidates
        formulae = []
        for fn in candidates:
            if os.path.isfile(fn):
                with open(fn, "rb") as f:
                    fs = json.loads(f.read().decode('utf-8'))
                for f in fs:
                    formulae.append(tuple(f))
        return formulae

    def set_site(self, site):
        """Set Nikola site object."""
        super(LatexImageFormulaRenderer, self).set_site(site)
        self.__formula_color = site.config.get('LATEX_FORMULA_COLOR', self.__formula_color)
        self.__formula_scale = site.config.get('LATEX_FORMULA_SCALE', self.__formula_scale)
        self.__extra_formula_sources = os.path.join(site.config['CACHE_FOLDER'], 'extra-formula-sources')

        if not hasattr(site, 'latex_formula_collectors'):
            site.latex_formula_collectors = []
        site.latex_formula_collectors.append(self._collect_formulas)

    def create_context(self):
        """Create a FormulaContext object."""
        return FormulaContext(self.__formula_scale, self.__formula_color)

    def get_extra_targets(self, post, lang, dest):
        """Return a list of extra formula-related targets."""
        return [self._get_formulae_filename(post, lang)]

    def add_extra_deps(self, post, lang, what, where):
        """Return a list of extra dependencies for given post and language."""
        if what == 'uptodate' and where == 'fragment':
            return [nikola.utils.config_changed({
                'scale': self.__formula_scale,
                'color': list(self.__formula_color),
            }, 'latex_formula_image_renderer:config')]
        return []

    def _write_formulae(self, latex_context, filename):
        """Write used LaTeX formulae into JSON-encoded file."""
        formulae = sorted(latex_context.get_plugin_data(self.name, 'formulae', []))
        with open(filename, "wb") as f:
            f.write(json.dumps(formulae, sort_keys=True).encode('utf-8'))

    def write_extra_targets(self, post, lang, dest, latex_context):
        """Write extra formula-related targets."""
        self._write_formulae(latex_context, self._get_formulae_filename(post, lang))

    def before_processing(self, latex_context, source_path=None, post=None):
        """Add information to context before post is processed."""
        latex_context.store_plugin_data(self.name, 'formulae', [])

    def after_processing(self, latex_context, source_path=None, post=None):
        """Retrieve information from context after post is processed."""
        if post is None and source_path is not None:
            fn = os.path.join(self.__extra_formula_sources, source_path, '.texfor')
            nikola.utils.makedirs(os.path.split(fn)[0])
            self._write_formulae(latex_context, fn)

    def modify_result(self, output, latex_context):
        """Modify generated HTML output."""
        return output

    def render(self, formula, formula_context, formula_type, latex_context):
        """Produce HTML code which displays the formula.

        formula: LaTeX code for the formula (excluding environment/delimiters)
        formula_context: a FormulaContext object created by this object (or a clone of it)
        formula_type: one of 'inline', 'display', 'align', 'pstricks', 'tikzpicture'
        latex_context: the LaTeX context object
        """
        try:
            lfr = self.site.latex_formula_renderer
        except:
            LOGGER.error("Cannot find latex formula rendering plugin!")
            sys.exit(1)
        src, width, height = lfr.compile(formula, formula_context.color, formula_context.scale, formula_type)
        latex_context.get_plugin_data(self.name, 'formulae', []).append((formula, formula_context.color, formula_context.scale, formula_type))
        alt_text = _escape_html_argument(formula).strip()
        css_type = formula_type
        return "<img class='img-{0}-formula img-formula' width='{1}' height='{2}' src='{3}' alt='{4}' title='{4}' />".format(css_type, width, height, src, alt_text)
