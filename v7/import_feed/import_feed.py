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
import datetime
import os
import time

try:
    from urlparse import urlparse, urlunparse
except ImportError:
    from urllib.parse import urlparse, urlunparse  # NOQA

try:
    import feedparser
except ImportError:
    feedparser = None  # NOQA

from nikola.plugin_categories import Command
from nikola import utils
from nikola.utils import req_missing
from nikola.plugins.basic_import import ImportMixin
from nikola.plugins.command.init import SAMPLE_CONF, prepare_config

LOGGER = utils.get_logger('import_feed', utils.STDERR_HANDLER)


class CommandImportFeed(Command, ImportMixin):
    """Import a feed dump."""

    name = "import_feed"
    needs_config = False
    doc_usage = "[options] --url=feed_url"
    doc_purpose = "import a RSS/Atom feed"
    cmd_options = [
        {
            'name': 'output_folder',
            'long': 'output-folder',
            'short': 'o',
            'default': '../new_site',
            'help': 'Location to write imported content.'
        },
        {
            'name': 'base_name',
            'long': 'base-name',
            'short': 'b',
            'default': 'posts',
            'help': 'Top folder of the blog posts URL'
        },
        {
            'name': 'url',
            'long': 'url',
            'short': 'u',
            'default': None,
            'help': 'URL or filename of the feed to be imported.'
        },
    ]

    def _execute(self, options, args):
        '''
            Import Atom/RSS feed
        '''
        if feedparser is None:
            req_missing(['feedparser'], 'import feeds')
            return

        if not options['url']:
            print(self.help())
            return

        self.feed_url = options['url']
        self.base_name = options['base_name']
        self.output_folder = options['output_folder']
        self.import_into_existing_site = False
        self.url_map = {}
        channel = self.get_channel_from_file(self.feed_url)
        self.context = self.populate_context(channel, self.base_name)
        conf_template = self.generate_base_site()

        self.import_posts(channel)

        self.context['REDIRECTIONS'] = self.configure_redirections(
            self.url_map)

        self.write_configuration(self.get_configuration_output_path(
        ), conf_template.render(**prepare_config(self.context)))

    @classmethod
    def get_channel_from_file(cls, filename):
        return feedparser.parse(filename)

    @staticmethod
    def populate_context(channel, base_name):
        context = SAMPLE_CONF.copy()
        context['DEFAULT_LANG'] = channel.feed.title_detail.language \
            if channel.feed.title_detail.language else 'en'
        context['BLOG_TITLE'] = channel.feed.title

        context['BLOG_DESCRIPTION'] = channel.feed.get('subtitle', '')
        site_url = urlparse(channel.feed.get('link', ''))
        site_url = site_url._replace(path="/", params="", query="", fragment="")
        context['SITE_URL'] = urlunparse(site_url)
        context['BASE_URL'] = channel.feed.get('link', '')
        context['BLOG_EMAIL'] = channel.feed.author_detail.get('email', '') if 'author_detail' in channel.feed else ''
        context['BLOG_AUTHOR'] = channel.feed.author_detail.get('name', '') if 'author_detail' in channel.feed else ''

        context['POSTS'] = '''(
            ("{0}/*.html", "{0}", "post.tmpl"),
        )'''.format(base_name)
        context['PAGES'] = '''(
            ("stories/*.html", "stories", "story.tmpl"),
        )'''
        context['COMPILERS'] = '''{
        "rest": ('.txt', '.rst'),
        "markdown": ('.md', '.mdown', '.markdown', '.wp'),
        "html": ('.html', '.htm')
        }
        '''

        return context

    def import_posts(self, channel):
        for item in channel.entries:
            self.process_item(item)

    def process_item(self, item):
        self.import_item(item, self.base_name)

    def import_item(self, item, out_folder):
        """Takes an item from the feed and creates a post file."""

        # link is something like http://foo.com/2012/09/01/hello-world/
        # So, lets remove the BASE_URL from it to get real path
        link = item.link

        # TODO - link may be without domain

        if not link.startswith(self.context["BASE_URL"]):
            LOGGER.error("Foreign URL found in feed: %s", link)
            return

        link_path = link[len(self.context["BASE_URL"]):]

        title = item.title

        # blogger supports empty titles, which Nikola doesn't
        if not title:
            LOGGER.warn("Empty title in post with URL {0}. Using NO_TITLE "
                        "as placeholder, please fix.".format(link))
            title = "NO_TITLE"


        file_path = os.path.join(*[utils.slugify(x) for x in link_path.split("/")])
        file_path = os.path.join(out_folder, file_path)

        if "/" + file_path != urlparse(link).path:
            LOGGER.info("URL moved from %s to %s", urlparse(link).path, file_path)
            do_link = True
        else:
            do_link = False

        if file_path.endswith("/"):
            file_path += "index.html"
        slug = utils.slugify(link_path)

        description = ''
        try:
            post_date = datetime.datetime.fromtimestamp(time.mktime(
                item.published_parsed))
        except AttributeError:
            post_date = datetime.datetime.fromtimestamp(time.mktime(
                item.modified_parsed))
        if item.get('content'):
            for candidate in item.get('content', []):
                content = candidate.value
                break
                #  FIXME: handle attachments
        elif item.get('summary'):
            content = item.get('summary')
        else:
            content = ''
            LOGGER.warn('Entry without content! {}', item)

        tags = []
        for tag in item.get('tags', []):
            tags.append(tag.term)

        if item.get('app_draft'):
            tags.append('draft')
            is_draft = True
        else:
            is_draft = False

        if is_draft and self.exclude_drafts:
            LOGGER.notice('Draft "{0}" will not be imported.'.format(title))
        elif content.strip():
            # If no content is found, no files are written.
            content = self.transform_content(content)

            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            self.write_metadata(os.path.join(self.output_folder, file_path[:-len(".html")] + '.meta'),
                                title, "", post_date, description, tags)
            self.write_content(os.path.join(self.output_folder, file_path), content)
            if do_link:
                self.url_map[urlparse(link).path] = "/" + file_path
        else:
            LOGGER.warn('Not going to import "{0}" because it seems to contain'
                        ' no content.'.format(title))

    def write_metadata(self, filename, title, slug, post_date, description, tags):
        super(CommandImportFeed, self).write_metadata(
            filename,
            title,
            slug,
            post_date.strftime(r'%Y/%m/%d %H:%m:%S'),
            description,
            tags)
