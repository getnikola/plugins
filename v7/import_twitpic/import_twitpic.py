# -*- coding: utf-8 -*-

# Copyright © 2015 Juanjo Conti.

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
import datetime
import re

from nikola.plugin_categories import Command
from nikola import utils
from nikola.plugins.basic_import import ImportMixin

LOGGER = utils.get_logger('import_twitpic', utils.STDERR_HANDLER)

twitter_username = re.compile(r'@([A-Za-z0-9_]+)')
twitter_hashtag = re.compile(r'#([A-Za-z0-9_]+)')


class CommandImportTwitpic(Command, ImportMixin):
    """Import from Twitpic."""

    name = "import_twitpic"
    needs_config = False
    doc_usage = "[options] folder"
    doc_purpose = "import from Twitpic"
    cmd_options = [
        {
            'name': 'output_folder',
            'long': 'output-folder',
            'short': 'o',
            'default': 'posts',
            'help': 'Location to write imported content.'
        },
        {
            'name': 'tags',
            'long': 'tags',
            'short': 't',
            'default': '',
            'help': 'Tags to add to all new posts. Comma separated.'
        },
    ]

    def _execute(self, options, args):
        """Import from Twitpic."""

        if not args:
            print(self.help())
            return

        options['filename'] = args[0]
        self.path = options['filename']
        self.output_folder = options['output_folder']
        self.extra_tags = [t.strip() for t in options['tags'].split(",")]
        self.import_into_existing_site = True
        with open(os.path.join(self.path, 'tweets.txt')) as f:
            chunks = [p.strip() for p in f.read().decode('utf-8').split("\n\n") if p != '\n']
            self.site.scan_posts()
            self.site_tags = {utils.slugify(t): t for t in self.site.posts_per_tag}
            self.import_pics(chunks)

    def import_pics(self, chunks):
        for c in chunks:
            head_and_text = c.split('\n')
            pic, date = head_and_text[0].split(" on: ")
            text = ''
            if len(head_and_text) == 2:
                text = head_and_text[1]
            self.import_item(pic, date, text)

    def import_item(self, pic, date, text):
        """Create a post file."""

        post_date = datetime.datetime.strptime(date, "%m/%d/%Y")
        title = "Twitpic: %s" % post_date.strftime("%d/%m/%Y")
        slug = utils.slugify(title)
        self.tags = ["Twitpic"] + self.extra_tags
        content = self.expand(text)
        base, ext = pic.split('.')
        content += """

.. figure:: %s.thumbnail.%s
  :target: %s
""" % (base, ext, pic)

        self.write_metadata(
            os.path.join(self.output_folder, slug + '.meta'),
            title, slug, post_date.strftime(r'%Y/%m/%d %H:%m:%S'), '', self.tags)
        self.write_content(
            os.path.join(self.output_folder, slug + '.rst'),
            content,
            False)
        utils.copy_file(os.path.join(self.path, pic), os.path.join("images", self.output_folder, slug, pic))

    def expand(self, text):
        """Add links to the text and collect tags for the post."""

        def _username(m):
            self.add_tag(m.group(1))
            return '`%s <https://twitter.com/%s>`_' % (m.group(0), m.group(1))

        text = twitter_username.sub(_username, text)

        def _hashtag(m):
            self.add_tag(m.group(1))
            return '`%s <https://twitter.com/hashtag/%s>`_' % (m.group(0), m.group(1))

        return twitter_hashtag.sub(_hashtag, text)

    def add_tag(self, tag):
        """If a similar tag is already present in the site, use that."""

        self.tags.append(self.site_tags.get(utils.slugify(tag), tag))
