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

import os
import subprocess
from nikola.plugin_categories import Command
from nikola import utils

DATO_CONFIG = '''
// dato.config.js

module.exports = (dato, root, i18n) => {

  root.directory("dato/posts", (postsDir) => {
    // ...iterate over the "Blog post" records...
    dato.posts.forEach((post) => {
      // ...and create a markdown file for each article!
      postsDir.createPost(
        `${post.slug}.md`, "yaml", {
          frontmatter: {
            title: post.title,
            date: post.date,
            tags: post.tags,
            author: post.author,
            description: post.description,
            category: post.category,
          },
        content: post.content
        }
      );
    });
  });

  root.directory("dato/pages", (pagesDir) => {
    // ...iterate over the "Pages" records...
    dato.pages.forEach((page) => {
      // ...and create a markdown file for each article!
      pagesDir.createPost(
        `${page.slug}.md`, "yaml", {
          frontmatter: {
            title: page.title,
            author: page.author,
            description: page.description,
          },
        content: page.content
        }
      );
    });
  });


};
'''

LOGGER = utils.get_logger('datocms', utils.STDERR_HANDLER)


class CommandDatoCMS(Command):
    """Import the DatoCMS dump."""

    name = "datocms"
    needs_config = True
    doc_usage = ""
    doc_purpose = "import the DatoCMS dump"

    def _execute(self, options, args):
        """Import posts and pages from DatoCMS."""
        if not os.path.exists('dato.config.js'):
            with open('dato.config.js') as outf:
                outf.write(DATO_CONFIG)
        subprocess.call(['./node_modules/.bin/dato', 'dump'])
