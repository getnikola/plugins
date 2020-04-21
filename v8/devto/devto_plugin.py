# -*- coding: utf-8 -*-

# Copyright © 2020 Roberto Alsina and others.

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


from __future__ import print_function, unicode_literals

import json
import os

import pypandoc
import pydevto

from nikola import utils
from nikola.plugin_categories import Command

LOGGER = utils.get_logger('Devto')


class CommandDevto(Command):
    """
    This class is based on the package medium (https://plugins.getnikola.com/v8/medium/)
    """

    name = "devto"
    needs_config = True
    doc_usage = ""
    doc_purpose = "Publish your articles to Dev.to"

    def _execute(self, options, args):
        """Publish to Dev.to."""

        if not os.path.exists('devto.json'):
            LOGGER.error(
                'Please put your credentials in devto.json as described in the README.')
            return False
        with open('devto.json') as inf:
            creds = json.load(inf)
        api = pydevto.PyDevTo(api_key=creds['TOKEN'])

        articles = api.articles()
        self.site.scan_posts()

        posts = self.site.timeline
        toPost = [post for post in posts if not next((item for item in articles if item["title"] == post.title()), False) and post.meta('devto')]

        if len(toPost) == 0:
            print("Nothing new to post...")

        for post in toPost:
            if post.source_ext() == '.md':
                with open(post.source_path, 'r') as file:
                    data = file.readlines()
                    m_post = api.create_article(
                        title=post.title(),
                        body_markdown="".join(data),
                        published=True,
                        canonical_url=post.permalink(absolute=True),
                        tags=post.tags
                    )
                    print('Published %s to %s' %
                    (post.meta('slug'), m_post['url']))
            elif post.source_ext() == '.rst':
                m_post = api.create_article(
                    title=post.title(),
                    body_markdown = pypandoc.convert_file(post.source_path, to='gfm', format='rst'),
                    published=True,
                    canonical_url=post.permalink(absolute=True),
                    tags=post.tags
                )
                print('Published %s to %s' %
                (post.meta('slug'), m_post['url']))
