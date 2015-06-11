# -*- coding: utf-8 -*-

# Copyright © 2012-2014 Roberto Alsina and others.

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
import json
import os
try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse  # NOQA
from zipfile import ZipFile

import dateutil
try:
    import micawber
except ImportError:
    micawber = None  # NOQA

from nikola.plugin_categories import Command
from nikola import utils
from nikola.utils import req_missing
from nikola.plugins.basic_import import ImportMixin
from nikola.plugins.command.init import SAMPLE_CONF, prepare_config

LOGGER = utils.get_logger('import_gplus', utils.STDERR_HANDLER)


class CommandImportGplus(Command, ImportMixin):
    """Import a Google+ dump."""

    name = "import_gplus"
    needs_config = False
    doc_usage = "[options] dump_file.zip"
    doc_purpose = "import a Google+ dump"
    cmd_options = ImportMixin.cmd_options

    def _execute(self, options, args):
        '''
            Import Google+ dump
        '''

        if not args:
            print(self.help())
            return

        if micawber is None:
            req_missing(['micawber'], 'import from Google+')

        options['filename'] = args[0]
        self.export_file = options['filename']
        self.output_folder = options['output_folder']
        self.import_into_existing_site = False
        self.url_map = {}

        with ZipFile(self.export_file, 'r') as zipfile:
            gplus_names = [x for x in zipfile.namelist() if '/Google+ Stream/' in x]
            self.context = self.populate_context(zipfile, gplus_names)
            conf_template = self.generate_base_site()
            self.write_configuration(self.get_configuration_output_path(), conf_template.render(**prepare_config(self.context)))
            self.import_posts(zipfile, gplus_names)

    @staticmethod
    def populate_context(zipfile, names):
        # We don't get much data here
        context = SAMPLE_CONF.copy()
        context['DEFAULT_LANG'] = 'en'
        context['BLOG_DESCRIPTION'] = ''
        context['SITE_URL'] = 'http://example.com/'
        context['BLOG_EMAIL'] = ''

        # Get any random post, all have the same data
        with zipfile.open(names[0], 'r') as post_f:
            data = json.load(post_f)
            context['BLOG_TITLE'] = data['actor']['displayName']
            context['BLOG_AUTHOR'] = data['actor']['displayName']

        context['POSTS'] = '''(
            ("posts/*.html", "posts", "post.tmpl"),
            ("posts/*.rst", "posts", "post.tmpl"),
        )'''
        context['PAGES'] = '''(
            ("stories/*.html", "stories", "story.tmpl"),
            ("stories/*.rst", "stories", "story.tmpl"),
        )'''
        context['COMPILERS'] = '''{
        "rest": ('.txt', '.rst'),
        "html": ('.html', '.htm')
        }
        '''

        return context

    def import_posts(self, zipfile, names):
        """Import all posts."""
        out_folder = 'posts'
        providers = micawber.bootstrap_basic()
        for name in names:
            with zipfile.open(name, 'r') as post_f:
                data = json.load(post_f)
                title = data['title']

                slug = utils.slugify(title)

                if not slug:  # should never happen
                    LOGGER.error("Error converting post:", title)
                    return

                description = ''
                post_date = dateutil.parser.parse(data["published"])
                content = data["object"]["content"]

                for obj in data["object"].get("attachments", []):
                    content += '\n<div> {} </div>\n'.format(micawber.parse_text(obj["url"], providers))

                tags = []
                self.write_metadata(os.path.join(self.output_folder, out_folder, slug + '.meta'), title, slug, post_date, description, tags)
                self.write_content(
                    os.path.join(self.output_folder, out_folder, slug + '.html'),
                    content)

    @staticmethod
    def write_metadata(filename, title, slug, post_date, description, tags):
        ImportMixin.write_metadata(filename,
                                   title,
                                   slug,
                                   post_date.strftime(r'%Y/%m/%d %H:%m:%S'),
                                   description,
                                   tags)
