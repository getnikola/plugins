# -*- coding: utf-8 -*-

# Copyright © 2016 Dean Wyatte
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

import lxml.html

try:
    from traitlets.config import Config
except ImportError:
    from IPython.config import Config

try:
    from nbconvert.exporters import HTMLExporter
except ImportError:
    from IPython.nbconvert.exporters import HTMLExporter

from nikola.plugin_categories import ShortcodePlugin


class NotebookShortcodePlugin(ShortcodePlugin):
    """ Notebook shortcode. """
    name = "notebook_shortcode"

    def set_site(self, site):
        super(NotebookShortcodePlugin, self).set_site(site)
        self.site.register_shortcode('notebook', self.render_notebook)

    def render_notebook(self, filename, site=None, data=None, lang=None, post=None):
        c = Config(self.site.config['IPYNB_CONFIG'])
        export_html = HTMLExporter(config=c)
        (notebook_raw, _) = export_html.from_filename(filename)

        # The raw HTML contains garbage (scripts and styles), we can’t leave it in
        notebook_html = lxml.html.fromstring(notebook_raw)
        notebook_code = lxml.html.tostring(notebook_html.xpath('//*[@id="notebook"]')[0], encoding='unicode')

        return notebook_code, [filename]
