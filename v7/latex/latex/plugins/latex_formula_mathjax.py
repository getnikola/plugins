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

"""Display formulas for LaTeX post compiler via MathJax."""

from __future__ import unicode_literals

import nikola.plugin_categories
import nikola.utils

LOGGER = nikola.utils.get_logger('compile_latex.formula.mathjax', nikola.utils.STDERR_HANDLER)


class FormulaContext(object):
    """Stores information about the formula renderer."""

    def clone(self):
        """Clone this FormulaContext object."""
        return FormulaContext()


class MathJaxFormulaRenderer(nikola.plugin_categories.CompilerExtension):
    """Show LaTeX formulae via MathJax. Supports only inline and display-style formulae."""

    name = 'latex_formula_mathjax'
    compiler_name = 'latex'
    latex_plugin_type = 'formula_renderer'

    def __init__(self):
        """Initialize plugin."""
        super(MathJaxFormulaRenderer, self).__init__()
        self.__script_origin = '//cdn.mathjax.org/mathjax/latest/MathJax.js'
        self.__delimiters = {
            'inline': r'\({0}\)',
            'display': r'$${0}$$'
        }

    def set_site(self, site):
        """Set Nikola site object."""
        super(MathJaxFormulaRenderer, self).set_site(site)
        self.__script_origin = site.config.get('LATEX_MATHJAX_SCRIPT_ORIGIN', self.__script_origin)

    def initialize(self, latex_compiler, latex_parsing_environment):
        """Initialize plugin.

        Called after set_site and before anything else is done.
        This can be used to extend the LaTeX parsing environment.
        """
        pass

    def create_context(self):
        """Create a FormulaContext object.

        Only used for formula rendering plugins (i.e.
        when ``latex_plugin_type == 'formula_renderer'``).
        """
        return FormulaContext()

    def get_extra_targets(self, post, lang, dest):
        """Return a list of extra targets."""
        return []

    def add_extra_deps(self, post, lang, what, where):
        """Return a list of extra dependencies for given post and language."""
        if what == 'uptodate' and where == 'fragment':
            return [nikola.utils.config_changed({
                'script_origin': self.__script_origin,
                'delimiters': self.__delimiters,
            }, 'latex_formula_mathjax:config')]
        return []

    def write_extra_targets(self, post, lang, dest, latex_context):
        """Write extra targets."""
        pass

    def before_processing(self, latex_context, source_path=None, post=None):
        """Add information to context before post is processed."""
        pass

    def after_processing(self, latex_context, source_path=None, post=None):
        """Retrieve information from context after post is processed."""
        pass

    def modify_html_output(self, output, latex_context):
        """Modify generated HTML output."""
        prefix = '''<script type="text/x-mathjax-config">MathJax.Hub.Config({tex2jax: {inlineMath: [['\\\\(','\\\\)']]}});</script>'''
        prefix += '''<script type="application/javascript" src="''' + self.__script_origin + '''?config=TeX-AMS_HTML-full"></script>'''
        return prefix + output

    def render(self, formula, formula_context, formula_type, latex_context):
        """Produce HTML code which displays the formula.

        formula: LaTeX code for the formula (excluding environment/delimiters)
        formula_context: a FormulaContext object created by this object (or a clone of it)
        formula_type: one of 'inline', 'display', 'align', 'pstricks', 'tikzpicture'
        latex_context: the LaTeX context object

        Only used for formula rendering plugins (i.e.
        when ``latex_plugin_type == 'formula_renderer'``).
        """
        if formula_type not in self.__delimiters:
            raise NotImplementedError("Formula type '{}' is not supported by MathJax formula rendering backend!".format(formula_type))

        return self.__delimiters[formula_type].format(formula)
