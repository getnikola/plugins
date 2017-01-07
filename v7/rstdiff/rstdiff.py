# -*- coding: utf-8 -*-

# Copyright © 2014 Roberto Alsina

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

from difflib import HtmlDiff

from docutils import nodes
from docutils.parsers.rst import Directive, directives

from nikola.plugin_categories import RestExtension


class Plugin(RestExtension):

    name = "rstdiff"

    def set_site(self, site):
        self.site = site
        directives.register_directive('diff', Diff)
        return super(Plugin, self).set_site(site)


class Diff(Directive):
    """Restructured Text extension to display files side-by-side."""

    has_content = False
    required_arguments = 0
    option_spec = {
        "left": directives.unchanged,
        "right": directives.unchanged,
    }

    def run(self):
        with open(self.options['left']) as left:
            left_lines = left.readlines()
        with open(self.options['right']) as right:
            right_lines = right.readlines()
        diff = HtmlDiff()
        return [nodes.raw('', diff.make_table(left_lines, right_lines), format='html')]
