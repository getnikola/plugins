# -*- coding: utf-8 -*-

# Copyright © 2025 Roberto Alsina and others

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

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None
import requests
import sys

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
    """Import a Page."""

    name = "import_page"
    needs_config = False
    doc_usage = "[options] page_url [page_url,...]"
    doc_purpose = "import arbitrary web pages"

    def _execute(self, options, args):
        """Import a Page."""
        if BeautifulSoup is None:
            utils.req_missing(['bs4'], 'use the import_page plugin')
        for url in args:
            self._import_page(url)

    def _import_page(self, url):
        parse = requests.utils.urlparse(url)
        if 'http' in parse.scheme:
            r = requests.get(url)
            if not (199 < r.status_code < 300):  # Did not get it
                LOGGER.error(f'Error fetching URL: {url}')
                return 1
            html = r.content
        else:
            try:
                with open(url, 'rb') as f:
                    html = f.read()
            except FileNotFoundError:
                LOGGER.error(f'Error file does not exist: {url}')
                return 1
            except (OSError, IOError) as e:
                LOGGER.error(f'Error opening file "{url}": {e}')
                return 1

        try:
            soup = BeautifulSoup(html, "lxml")
        except ImportError:
            soup = BeautifulSoup(html, "html.parser")

        title = soup.title.text if soup.title else "Untitled Page"
        try:
            slug = utils.slugify(title, lang='')
        except TypeError:
            slug = utils.slugify(title)

        candidates = soup.find_all(["p", "div", "article", "section"])
        if candidates:
            node = max(candidates, key=lambda n: len(n.get_text(strip=True)))
        else:
            node = None  # empty

        document = doc_template.format(
            title=title,
            slug=slug,
            content=node.prettify()
        )
        with codecs.open(slug + '.html', 'w+', encoding='utf-8') as outf:
            outf.write(document)
