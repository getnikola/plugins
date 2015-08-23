# -*- coding: utf-8 -*-

# Copyright © 2014, 2015 Miguel Ángel García

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

from __future__ import unicode_literals, print_function

import codecs

import libextract.api
import lxml.html
import requests

from nikola.plugin_categories import Command
from nikola import utils

LOGGER = utils.get_logger('import_page', utils.STDERR_HANDLER)


doc_template = '''<!--
.. title: {title}
.. slug: {slug}
-->

{content}
'''

class CommandImportPage(Command):
    """Import a Page or Octopress blog."""

    name = "import_page"
    needs_config = False
    doc_usage = "[options] page_url [page_url,...]"
    doc_purpose = "import arbitrary web pages"

    def _execute(self, options, args):
        """Import a Page."""
        for url in args:
            self._import_page(url)

    def _import_page(self, url):
        r = requests.get('http://en.wikipedia.org/wiki/Information_extraction')
        if 199 < r.status_code < 300:  # Got it
            # Use the page's title
            doc = lxml.html.fromstring(r.content)
            title = doc.find('*//title').text_content().decode('utf-8')
            slug = utils.slugify(title)
            nodes = list(libextract.api.extract(r.content))
            # Let's assume the node with more text is the good one
            lengths = [len(n.text_content()) for n in nodes]
            node = nodes[lengths.index(max(lengths))]
            document = doc_template.format(
                title = title,
                slug = slug,
                content = lxml.html.tostring(node, encoding='utf8', method='html', pretty_print=True).decode('utf8')
            )
            with codecs.open(slug + '.html', 'w+', encoding='utf-8' ) as outf:
                outf.write(document)

        else:
            LOGGER.error('Error fetching URL: {}'.format(url))
