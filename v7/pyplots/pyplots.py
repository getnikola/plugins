# -*- coding: utf-8 -*-

# Copyright © 2012-2015 Roberto Alsina and others.

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

from hashlib import md5
import io
import os

from docutils import nodes
from docutils.parsers.rst import directives
try:
    import matplotlib
    import matplotlib._pylab_helpers
    import matplotlib.pyplot as plt
except ImportError:
    matplotlib = None

from nikola.plugin_categories import RestExtension
from nikola.utils import req_missing, makedirs

_site = None


class Plugin(RestExtension):

    name = "pyplots"

    def set_site(self, site):
        global _site
        _site = self.site = site
        directives.register_directive('plot', PyPlot)
        PyPlot.out_dir = os.path.join(site.config['OUTPUT_FOLDER'], 'pyplots')
        return super(Plugin, self).set_site(site)

pyplot_spec = directives.images.Image.option_spec
pyplot_spec['include-source'] = directives.flag


class PyPlot(directives.images.Image):
    """ Reimplementation of http://matplotlib.org/sampledoc/extensions.html#inserting-matplotlib-plots."""

    has_content = True
    option_spec = pyplot_spec
    optional_arguments = 1
    required_arguments = 0

    def run(self):
        if matplotlib is None:
            msg = req_missing(['matplotlib'], 'use the plot directive', optional=True)
            return [nodes.raw('', '<div class="text-error">{0}</div>'.format(msg), format='html')]

        if not self.arguments and not self.content:
            raise self.error('The plot directive needs either an argument or content.')

        if self.arguments and self.content:
            raise self.error('The plot directive needs either an argument or content, not both.')

        if self.arguments:
            plot_path = self.arguments[0]
            with io.open(plot_path, encoding='utf-8') as fd:
                data = fd.read()
        elif self.content:
            data = '\n'.join(self.content)
            plot_path = md5(data).hexdigest()

        # Always reset context
        plt.close('all')
        matplotlib.rc_file_defaults()
        # Run plot
        exec(data)

        out_path = os.path.join(self.out_dir, plot_path + '.svg')
        plot_url = '/' + os.path.join('pyplots', plot_path + '.svg').replace(os.sep, '/')

        figures = [manager.canvas.figure for manager in matplotlib._pylab_helpers.Gcf.get_all_fig_managers()]
        for figure in figures:
            makedirs(os.path.dirname(out_path))
            figure.savefig(out_path, format='svg')  # Yes, if there's more than one, it's overwritten, sucks.
        self.arguments = [plot_url]
        return super(PyPlot, self).run()
