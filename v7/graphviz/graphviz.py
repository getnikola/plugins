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

import hashlib
import os
from subprocess import Popen, PIPE

from docutils import nodes
from docutils.parsers.rst import Directive, directives
from docutils.statemachine import StringList

from nikola.plugin_categories import RestExtension
from nikola.utils import LOGGER, makedirs


class Plugin(RestExtension):

    name = "rest_graphviz"

    def set_site(self, site):
        self.site = site
        directives.register_directive('graphviz', Graphviz)
        directives.register_directive('graph', Graph)
        directives.register_directive('digraph', DiGraph)
        Graphviz.embed_graph = self.site.config.get('GRAPHVIZ_EMBED', True)
        Graphviz.output_folder = self.site.config.get('GRAPHVIZ_OUTPUT', 'output/assets/graphviz')
        Graphviz.graph_path = self.site.config.get('GRAPHVIZ_GRAPH_PATH', '/assets/graphviz/')
        Graphviz.dot_path = self.site.config.get('GRAPHVIZ_DOT', 'dot')
        return super(Plugin, self).set_site(site)


class Graphviz(Directive):
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
    ignore_alt = True
    option_spec = {
        'alt': directives.unchanged,
        'inline': directives.flag,
        'caption': directives.unchanged,
    }

    def run(self):
        if 'alt' in self.options and self.ignore_alt:
            LOGGER.warning("Graphviz: the :alt: option is ignored, it's better to set the title of your graph.")
        if self.arguments:
            if self.content:
                LOGGER.warning("Graphviz: this directive can't have both content and a filename argument. Ignoring content.")
            f_name = self.arguments[0]
            # TODO: be smart about where exactly that file is located
            with open(f_name, 'rb') as inf:
                data = inf.read().decode('utf-8')
        else:
            data = '\n'.join(self.content)
        node_list = []
        try:
            p = Popen([self.dot_path, '-Tsvg'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
            svg_data, errors = p.communicate(input=data.encode('utf8'))
            code = p.wait()
            if code:  # Some error
                document = self.state.document
                return [document.reporter.error(
                        'Error processing graph: {0}'.format(errors), line=self.lineno)]
            if self.embed_graph:  # SVG embedded in the HTML
                if 'inline' in self.options:
                    svg_data = '<span class="graphviz">{0}</span>'.format(svg_data)
                else:
                    svg_data = '<p class="graphviz">{0}</p>'.format(svg_data)

            else:  # External SVG file
                # TODO: there is no reason why this branch needs to be a raw
                # directive. It could generate regular docutils nodes and
                # be useful for any writer.
                makedirs(self.output_folder)
                f_name = hashlib.md5(svg_data).hexdigest() + '.svg'
                img_path = self.graph_path + f_name
                f_path = os.path.join(self.output_folder, f_name)
                alt = self.options.get('alt', '')
                with open(f_path, 'wb+') as outf:
                    outf.write(svg_data)
                    self.state.document.settings.record_dependencies.add(f_path)
                if 'inline' in self.options:
                    svg_data = '<span class="graphviz"><img src="{0}" alt="{1}"></span>'.format(img_path, alt)
                else:
                    svg_data = '<p class="graphviz"><img src="{0}" alt="{1}"></p>'.format(img_path, alt)

            node_list.append(nodes.raw('', svg_data, format='html'))
            if 'caption' in self.options and 'inline' not in self.options:
                node_list.append(
                    nodes.raw('', '<p class="caption">{0}</p>'.format(self.options['caption']),
                              format='html'))
            return node_list
        except OSError:
            LOGGER.error("Can't execute 'dot'")
            raise


class Graph(Graphviz):
    ignore_alt = False

    def run(self):
        self.content = StringList(['graph "{0}" {{'.format(self.options.get('alt', ''))]) + self.content + StringList(['};'])
        return super(Graph, self).run()


class DiGraph(Graphviz):
    ignore_alt = False

    def run(self):
        self.content = StringList(['digraph "{0}" {{'.format(self.options.get('alt', ''))]) + self.content + StringList(['};'])
        return super(DiGraph, self).run()
