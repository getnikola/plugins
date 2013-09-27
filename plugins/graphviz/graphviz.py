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
from nikola.utils import LOGGER


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
    option_spec = {
        'alt': directives.unchanged,
        'inline': directives.flag,
        'caption': directives.unchanged,
    }

    def run(self):
        if 'alt' in self.options:
            LOGGER.warning("Graphviz: the :alt: option is ignored, it's better to set the title of your graph.")
        data = '\n'.join(self.content)
        node_list = []
        try:
            p = Popen(['dot', '-Tsvg'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
            svg_data, errors = p.communicate(input=data)
            code = p.wait()
            if code:  # Some error
                document = self.state.document
                return [document.reporter.error(
                        'Error processing graph: {0}'.format(errors), line=self.lineno)]

            if 'inline' in self.options:
                svg_data = '<span class="graphviz">{0}</span>'.format(svg_data)
            else:
                svg_data = '<p class="graphviz">{0}</p>'.format(svg_data)

            node_list.append(nodes.raw('', svg_data, format='html'))
            if 'caption' in self.options and 'inline' not in self.options:
                node_list.append(
                    nodes.raw('', '<p class="caption">{0}</p>'.format(self.options['caption']),
                              format='html'))
            return node_list
        except OSError:
            LOGGER.error("Can't execute 'dot'")
            raise
