# Copyright © 2024 Harald Nezbeda

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

import os

import requests
import sys

from nikola.plugin_categories import Command
from nikola.plugins.basic_import import ImportMixin
from nikola import utils

LOGGER = utils.get_logger('import_bookstack', utils.STDERR_HANDLER)


class CommandImportPage(Command, ImportMixin):
    """Import a Page."""

    name = "import_bookstack"
    needs_config = False
    doc_usage = "[options] page_url [page_url,...]"
    doc_purpose = "import arbitrary web pages"
    cmd_options = [
        {
            'name': 'output',
            'long': 'output',
            'short': 'o',
            'default': 'posts',
            'help': 'Location to write imported content.'
        },
        {
            'name': 'url',
            'long': 'url',
            'short': 'u',
            'default': None,
            'help': 'Bookstack Base URL.'
        },
        {
            'name': 'key',
            'long': 'key',
            'short': 'k',
            'default': None,
            'help': 'Bookstack API Key.'
        },
        {
            'name': 'book',
            'long': 'book',
            'short': 'b',
            'default': None,
            'help': 'Bookstack Book ID.'
        },
        {
            'name': 'chapter',
            'long': 'chapter',
            'short': 'c',
            'default': None,
            'help': 'Bookstack Chapter ID.'
        },
        {
            'name': 'page',
            'long': 'page',
            'short': 'p',
            'default': None,
            'help': 'Bookstack Page ID.'
        }
    ]

    def _execute(self, options, args):
        self.output = options['output']
        self.url = options['url']
        self.key = options['key']
        self.book = options['book']
        self.chapter = options['chapter']
        self.page = options['page']

        if not self.url:
            LOGGER.error("Bookstack Base URL is required.")
            sys.exit(1)

        if not self.key:
            LOGGER.error("Bookstack API Key is required.")
            sys.exit(1)

        if sum([bool(self.book), bool(self.chapter), bool(self.page)]) != 1:
            LOGGER.error("Only one of Bookstack Book ID, Chapter ID, or Page ID should be provided.")
            sys.exit(1)

        if self.page:
            self._import_page(self.page)
        elif self.chapter:
            self._import_chapter(self.chapter)
        elif self.book:
            self._import_book(self.book)

    def _bookstack_request(self, url):
        headers = {
            'Authorization': f'Token {self.key}'
        }
        return requests.get(url, headers=headers)

    def _import_page(self, page):
        response = self._bookstack_request(f"{self.url}/api/pages/{page}")

        if response.status_code == 200:
            page_data = response.json()

            if not page_data['draft']:
                slug = page_data['slug']
                title = page_data['name']
                content = page_data['html']
                post_date = page_data['created_at']
                description = page_data['name']
                tags = [tag['name'] for tag in page_data['tags']]

                self.write_metadata(
                    os.path.join(self.output,slug + '.meta'),
                    title,
                    slug,
                    post_date,
                    description,
                    tags
                )
                self.write_content(
                    os.path.join(self.output,slug + '.html'),
                    content
                )

        else:
            LOGGER.error(f"Failed to fetch page data: {response.status_code}")
            sys.exit(1)

    def _import_chapter(self, chpater):
        response = self._bookstack_request(f"{self.url}/api/chapters/{chpater}")

        if response.status_code == 200:
            chapter_data = response.json()
            for page in chapter_data['pages']:
                self._import_page(page['id'])

        else:
            LOGGER.error(f"Failed to fetch chapter data: {response.status_code}")
            sys.exit(1)

    def _import_book(self, book):
        response = self._bookstack_request(f"{self.url}/api/books/{book}")

        if response.status_code == 200:
            book_data = response.json()
            for content in book_data['contents']:
                if content['type'] == 'page':
                    self._import_page(content['id'])
                elif content['type'] == 'chapter':
                    self._import_chapter(content['id'])
        else:
            LOGGER.error(f"Failed to fetch book data: {response.status_code}")
            sys.exit(1)
