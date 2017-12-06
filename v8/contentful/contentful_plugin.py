# -*- coding: utf-8 -*-

# Copyright © 2017 Roberto Alsina and others.

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

import contentful
import yaml

from nikola import utils
from nikola.plugin_categories import Command

LOGGER = utils.get_logger('contentful', utils.STDERR_HANDLER)


class CommandContenful(Command):
    """Import the contenful dump."""

    name = "contenful"
    needs_config = True
    doc_usage = ""
    doc_purpose = "import the contenful dump"

    def _execute(self, options, args):
        """Import posts and pages from contenful."""
        if not os.path.exists('contentful.json'):
            LOGGER.error('Please put your credentials in contentful.json as described in the README.')
            return False
        with open('contentful.json') as inf:
            creds = json.load(inf)

        client = contentful.Client(creds['SPACE_ID'], creds['ACCESS_TOKEN'])
        post_dir = os.path.join('contentful', 'posts')
        utils.makedirs(post_dir)
        for post in client.entries({'content_type': 'post'}):
            fname = os.path.join(post_dir, post.slug + '.md')
            metadata = {k:v for k,v in post.fields().items() if k != 'content'}
            metadata['tags'] = ', '.join(metadata.get('tags', []))
            metadata['date'] = metadata['date'].isoformat()
            with open(fname, 'w+') as outf:
                outf.write('---\n')
                outf.write(yaml.dump(metadata, default_flow_style=False))
                outf.write('---\n\n')
                outf.write(post.content)

        page_dir = os.path.join('contentful', 'pages')
        utils.makedirs(page_dir)
        for page in client.entries({'content_type': 'page'}):
            metadata = {k:v for k,v in page.fields().items() if k != 'content'}
            fname = os.path.join(page_dir, page.slug + '.md')
            with open(fname, 'w+') as outf:
                outf.write('---\n')
                outf.write(yaml.dump(metadata, default_flow_style=False))
                outf.write('---\n\n')
                outf.write(page.content)
