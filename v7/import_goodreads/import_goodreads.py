# -*- coding: utf-8 -*-

# Copyright © 2012-2014 Juanjo Conti.

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
import os
import locale
import datetime

try:
    import feedparser
except ImportError:
    feedparser = None  # NOQA

from nikola.plugin_categories import Command
from nikola import utils
from nikola.utils import req_missing
from nikola.plugins.basic_import import ImportMixin

LOGGER = utils.get_logger('import_goodreads', utils.STDERR_HANDLER)

class CommandImportGoodreads(Command, ImportMixin):
    """Import a Goodreads RSS."""

    name = "import_goodreads"
    needs_config = False
    doc_usage = "[options] rss_url"
    doc_purpose = "import a Goodreads RSS"
    cmd_options = [
        {
            'name': 'output_folder',
            'long': 'output-folder',
            'short': 'o',
            'default': 'posts',
            'help': 'Location to write imported content.'
        },
    ]

    def _execute(self, options, args):
        """Import Goodreads RSS."""

        if feedparser is None:
            req_missing(['feedparser'], 'import Goodreads RSS')
            return

        if not args:
            print(self.help())
            return

        options['filename'] = args[0]
        self.feed_export_file = options['filename']
        self.output_folder = options['output_folder']
        self.import_into_existing_site = True
        channel = self.get_channel_from_file(self.feed_export_file)
        self.import_posts(channel)

    @classmethod
    def get_channel_from_file(cls, filename):
        return feedparser.parse(filename)

    def import_posts(self, channel):
        for item in channel.entries:
            self.process_item(item)

    def process_item(self, item):
        if item.user_read_at:   # Only import books finished
            self.import_item(item)

    def import_item(self, item):
        """Takes an item from the feed and creates a post file."""

        link = item.link
        if link.endswith('?utm_medium=api&utm_source=rss'):
            link = link[:-30]

        title = "Goodreads review: %s (%s)" % (item.title, item.author_name)

        slug = utils.slugify(title)

        # Needed because user_read_at can have a different locale
        saved = locale.getlocale(locale.LC_ALL)
        locale.setlocale(locale.LC_ALL, (None, None))
        post_date = datetime.datetime.strptime(item.user_read_at[:-6], "%a, %d %b %Y %H:%M:%S")
        locale.setlocale(locale.LC_ALL, saved)

        content = ''
        if item.get('user_review'):
            content = item.get('user_review')

        content += ("<br/><br/>" if content else "") + "Raiting: %s/5" % item.user_rating

        content += "<br/><br/>Original: <a href=\"%s\">%s</a>" % (link, link)

        tags = [item.author_name, item.title.replace(", ", " - "), "Goodreads review"]

        content = self.transform_content(content)

        self.write_metadata(
            os.path.join(self.output_folder, slug + '.meta'),
            title, slug, post_date, '', tags)
        self.write_content(
            os.path.join(self.output_folder, slug + '.html'),
            content)

    @staticmethod
    def write_metadata(filename, title, slug, post_date, description, tags):
        ImportMixin.write_metadata(filename,
                                   title,
                                   slug,
                                   post_date.strftime(r'%Y/%m/%d %H:%m:%S'),
                                   description,
                                   tags)
