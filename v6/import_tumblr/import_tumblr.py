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
from mako.template import Template

try:
    from urlparse import urlparse
    from urllib import unquote
except ImportError:
    from urllib.parse import urlparse, unquote  # NOQA

try:
    import pytumblr
except ImportError:
    pytumblr = None  # NOQA

try:
    import requests
except ImportError:
    requests = None  # NOQA

from nikola.plugin_categories import Command
from nikola import utils
from nikola.utils import req_missing
from nikola.plugins.basic_import import ImportMixin
from nikola.plugins.command.init import SAMPLE_CONF, prepare_config

LOGGER = utils.get_logger('import_tumblr', utils.STDERR_HANDLER)


class CommandImportTumblr(Command, ImportMixin):
    """Import a WordPress dump."""

    name = "import_tumblr"
    needs_config = False
    doc_usage = "[options] tumblr_blog_url"
    doc_purpose = "import a Tumblr blog"
    cmd_options = ImportMixin.cmd_options + [
        {
            'name': 'no_downloads',
            'long': 'no-downloads',
            'default': False,
            'type': bool,
            'help': "Do not try to download files for the import",
        },
    ]

    def _execute(self, options={}, args=[]):
        """Import a Tumblr blog into a Nikola site."""
        if not args:
            print(self.help())
            return

        options['site'] = args.pop(0)

        if args and ('output_folder' not in args or
                     options['output_folder'] == 'new_site'):
            options['output_folder'] = args.pop(0)

        if args:
            LOGGER.warn('You specified additional arguments ({0}). Please consider '
                        'putting these arguments before the filename if you '
                        'are running into problems.'.format(args))

        self.import_into_existing_site = False
        self.url_map = {}
        self.timezone = None

        self.tumblr_url = options['site']
        self.output_folder = options.get('output_folder', 'new_site')

        self.no_downloads = options.get('no_downloads', False)

        if pytumblr is None:
            req_missing(['pytumblr'], 'import a Tumblr site.')

        if requests is None:
            req_missing(['requests'], 'import a Tumblr site.')

        # Get site data via Tumblr API
        self.client = pytumblr.TumblrRestClient(
            'iEAu2WLA7GjLSZ81Ie5ZJ0h8Jochj5TzFurxRP8a54vwBOVDcC',
            'D9UkKOO9zq9VmqfNKEBZG61bwv9TMZjA4P07BkB6Y35GCfUCdJ',
            'QEOkjGsWtT2kUPUpoh6tHFGjwoycHSd7Ypz6G8Pgz31NbHjFEy',
            'wan0Pd7VzESpdLDN0FYqReFOE7U1GG2X0GknOuKT3kpNUHwkBK'
        )

        # Name of the site to import is the first part of the URL
        self.site_name = urlparse(self.tumblr_url).netloc.split('.')[0]
        self.site_info = self.client.blog_info(self.site_name)['blog']
        self.context = self.populate_context(self.site_info)
        self.context['SITE_URL'] = self.tumblr_url
        conf_template = self.generate_base_site()
        # Importing here because otherwise doit complains
        from nikola.plugins.compile.html import CompileHtml
        self.html_compiler = CompileHtml()
        self.import_posts()

        rendered_template = conf_template.render(**prepare_config(self.context))
        rendered_template = rendered_template.replace("# PRETTY_URLS = False", "PRETTY_URLS = True")
        self.write_configuration(self.get_configuration_output_path(),
                                 rendered_template)

    @staticmethod
    def populate_context(site_data):
        context = SAMPLE_CONF.copy()
        context['BLOG_TITLE'] = site_data['title']
        context['BLOG_DESCRIPTION'] = site_data['description']
        context['POSTS'] = '''(
            ("posts/*.html", "", "post.tmpl"),
        )'''
        context['COMPILERS'] = '''{
        "rest": ('.txt', '.rst'),
        "markdown": ('.md', '.mdown', '.markdown'),
        "html": ('.html', '.htm')
        }
        '''
        return context

    def download_url_content_to_file(self, url, dst_path):
        if self.no_downloads:
            return

        try:
            with open(dst_path, 'wb+') as fd:
                fd.write(requests.get(url).content)
        except requests.exceptions.ConnectionError as err:
            LOGGER.warn("Downloading {0} to {1} failed: {2}".format(url, dst_path, err))

    def import_posts(self):
        # First get all the posts
        post_count = self.site_info['posts']
        print('Getting %d posts' % post_count)
        self.posts = []
        for post_nr in range(0, post_count, 20):
            print('==> %d of %d' % (post_nr, post_count))
            self.posts.extend(self.client.posts(self.site_name, offset=post_nr)['posts'])

        for post in self.posts:
            if post['type'] == 'photo':
                self.import_photo(post)
            elif post['type'] == 'quote':
                self.import_quote(post)
            elif post['type'] == 'text':
                self.import_text(post)
            elif post['type'] == 'link':
                self.import_link(post)
            else:
                LOGGER.error("Don't know how to import posts of type %s" % post['type'])

    def import_photo(self, post):
        photos = post['photos']
        caption = post['caption']
        tags = post['tags']
        date = datetime.datetime.fromtimestamp(post['timestamp'])
        slug = post['slug']
        post_id = str(post['id'])  # URL is id/slug yeech
        content = Template(PHOTO_POST_TEMPLATE).render(**dict(
            photos=photos,
            caption=caption
        ))
        post_file = os.path.join(self.output_folder, 'posts', post_id, slug) + '.html'
        self.html_compiler.create_post(post_file, content=content, **{
            'tags': ','.join(tags),
            'title': 'photo',  # photo posts have no title
            'slug': slug,
            'date': date,
            'onefile': True,
            'hidetitle': True
        })

    def import_quote(self, post):
        quote = post['text']
        source = post['source']
        tags = post['tags']
        date = datetime.datetime.fromtimestamp(post['timestamp'])
        slug = post['slug']
        post_id = str(post['id'])  # URL is id/slug yeech
        content = Template(QUOTE_POST_TEMPLATE).render(**dict(
            quote=quote,
            source=source,
        ))
        post_file = os.path.join(self.output_folder, 'posts', post_id, slug) + '.html'
        self.html_compiler.create_post(post_file, content=content, **{
            'tags': ','.join(tags),
            'title': 'quote',  # photo posts have no title
            'slug': slug,
            'date': date,
            'onefile': True,
            'hidetitle': True
        })

    def import_text(self, post):
        title = post['title'] or 'title'
        tags = post['tags']
        date = datetime.datetime.fromtimestamp(post['timestamp'])
        slug = post['slug']
        post_id = str(post['id'])  # URL is id/slug yeech
        post_file = os.path.join(self.output_folder, 'posts', post_id, slug) + '.html'
        self.html_compiler.create_post(post_file, content=post['body'], **{
            'tags': ','.join(tags),
            'title': title,
            'slug': slug,
            'date': date,
            'onefile': True,
            'hidetitle': not post['title']
        })

    def import_link(self, post):
        url = post['url']
        description = post['description']
        title = post['title']
        tags = post['tags']
        date = datetime.datetime.fromtimestamp(post['timestamp'])
        slug = post['slug']
        post_id = str(post['id'])  # URL is id/slug yeech
        content = Template(LINK_POST_TEMPLATE).render(**dict(
            url=url,
            title=title,
            description=description,
        ))
        post_file = os.path.join(self.output_folder, 'posts', post_id, slug) + '.html'
        self.html_compiler.create_post(post_file, content=content, **{
            'tags': ','.join(tags),
            'title': post['title'] or 'title',
            'slug': slug,
            'date': date,
            'onefile': True,
            'hidetitle': not post['title']
        })


LINK_POST_TEMPLATE = '''
    <div class="link"><a href="${url}">${title}</a></div>
    <div class="description">
    ${description}
    </div>
'''

PHOTO_POST_TEMPLATE = '''
% for photo in photos:
    <div>
    <img class="figure" src="${photo['original_size']['url']}">
    % if photo['caption']:
    <span class="caption">${photo['caption']}</span>
    % endif
    </div>
% endfor
<span class="caption">${caption}</span>
'''

QUOTE_POST_TEMPLATE = '''
<span class="quote">${quote}</span></br>
<span class="caption">&mdash; ${source}</span>
'''
