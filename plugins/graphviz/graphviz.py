# -*- coding: utf-8 -*-

# Copyright © 2012-2013 Roberto Alsina and others.

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

from subprocess import Popen, PIPE

from docutils import nodes
from docutils.parsers.rst import Directive, directives

from nikola.plugin_categories import RestExtension


class Plugin(RestExtension):

    name = "rest_graphviz"

    def set_site(self, site):
        self.site = site
        directives.register_directive('graphviz', Graph)
        return super(Plugin, self).set_site(site)


class Graph(Directive):
    """ Restructured text extension for inserting graphs as SVG

        Usage:

            .. graphviz::

               digraph foo {
                   "bar" -> "baz";
               }
   """

    has_content = True
    required_arguments = 0
    optional_arguments = 1
    #option_spec = {
        #'embed': options.boolean
    #}

    def run(self):
        data = '\n'.join(self.content)
        p = Popen(['dot', '-Tsvg'], stdin=PIPE, stdout=PIPE)
        svg_data = p.communicate(input=data)[0]
        return [nodes.raw('', svg_data, format='html')]
