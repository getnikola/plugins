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


import json
import os

import pypandoc
import pydevto

from nikola import utils
from nikola.plugin_categories import Command

LOGGER = utils.get_logger("Devto")


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

        if not os.path.exists("devto.json"):
            LOGGER.error("Please put your credentials in devto.json as described in the README.")
            return False
        with open("devto.json") as inf:
            creds = json.load(inf)
        api = pydevto.PyDevTo(api_key=creds["TOKEN"])

        articles = api.articles()
        self.site.scan_posts()

        posts = self.site.timeline

        devto_titles = {item["title"] for item in articles}
        to_post = [
            post
            for post in posts
            if post.title() not in devto_titles and (post.meta("devto").lower() not in ["no", "false", "0"])
        ]

        if len(to_post) == 0:
            LOGGER.info("Nothing new to post...")

        for post in to_post:
            with open(post.source_path, "r") as file:
                data = file.read()

                if post.source_ext() == ".md":
                    content = "".join(data)
                elif post.source_ext() == ".rst":
                    content = pypandoc.convert_file(post.source_path, to="gfm", format="rst")

                m_post = api.create_article(
                    title=post.title(),
                    body_markdown=content,
                    published=True,
                    canonical_url=post.permalink(absolute=True),
                    tags=post.tags,
                )
                LOGGER.info("Published {} to {}".format(post.meta("slug"), m_post["url"]))
