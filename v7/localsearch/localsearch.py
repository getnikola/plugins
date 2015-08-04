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

from __future__ import unicode_literals
from copy import copy
import codecs
import json
import os

from doit.tools import result_dep

from nikola.plugin_categories import LateTask
from nikola.utils import config_changed, copy_tree, makedirs, LocaleBorg

# This is what we need to produce:
# var tipuesearch = {"pages": [
#     {"title": "Tipue Search, a jQuery site search engine", "text": "Tipue
#         Search is a site search engine jQuery plugin. It's free for both commercial and
#         non-commercial use and released under the MIT License. Tipue Search includes
#         features such as word stemming and word replacement.", "tags": "JavaScript",
#         "url": "http://www.tipue.com/search"},
#     {"title": "Tipue Search demo", "text": "Tipue Search demo. Tipue Search is
#         a site search engine jQuery plugin.", "tags": "JavaScript", "url":
#         "http://www.tipue.com/search/demo"},
#     {"title": "About Tipue", "text": "Tipue is a small web development/design
#         studio based in North London. We've been around for over a decade.", "tags": "",
#         "url": "http://www.tipue.com/about"}
# ]};


class TipueSearch(LateTask):
    """Render the blog posts as JSON data."""

    name = "local_search"

    def gen_tasks(self):
        self.site.scan_posts()

        kw = {
            "translations": self.site.config['TRANSLATIONS'],
            "output_folder": self.site.config['OUTPUT_FOLDER'],
        }

        posts = self.site.timeline[:]
        dst_json_path = os.path.join(kw["output_folder"], "assets", "js",
                                "tipuesearch_content.json")

        def save_data():
            pages = []
            for lang in kw["translations"]:
                for post in posts:
                    # Don't index drafts (Issue #387)
                    if post.is_draft or post.is_private or post.publish_later:
                        continue
                    text = post.text(lang, strip_html=True)
                    text = text.replace('^', '')

                    data = {}
                    data["title"] = post.title(lang)
                    data["text"] = text
                    data["tags"] = ",".join(post.tags)
                    data["url"] = post.permalink(lang)
                    pages.append(data)
            output = json.dumps({"pages": pages}, indent=2)
            makedirs(os.path.dirname(dst_json_path))
            with codecs.open(dst_json_path, "wb+", "utf8") as fd:
                fd.write(output)

        yield {
            "basename": str(self.name),
            "name": dst_json_path,
            "targets": [dst_json_path],
            "actions": [(save_data, [])],
            'uptodate': [config_changed(kw), result_dep('sitemap')]
        }
        # Note: The task should run everytime a new file is added or a
        # file is changed.  We cheat, and depend on the sitemap task,
        # to run everytime a new file is added.

        # Copy all the assets to the right places
        asset_folder = os.path.join(os.path.dirname(__file__), "files")
        for task in copy_tree(asset_folder, kw["output_folder"]):
            task["basename"] = str(self.name)
            yield task


# class TipueSearchHTML(LateTask):
#     """Render the blog posts as JSON data."""

#     name = "local_search_html"

#     def gen_tasks(self):
#         self.site.scan_posts()

#         kw = {
#             "translations": self.site.config['TRANSLATIONS'],
#             "output_folder": self.site.config['OUTPUT_FOLDER'],
#         }

        # FIXME: use a setting to define the path
        dst_html_path = os.path.join(kw["output_folder"], "search.html")

        def create_html():
            context = copy(self.site.GLOBAL_CONTEXT)
            context.update({
                'lang': LocaleBorg().current_lang,
                'title': 'Search',
                'permalink': '/search.html',
            })

            # from doit.tools import set_trace; set_trace()
            output = self.site.template_system.render_template(
                'search.tmpl', None, context
            )
            makedirs(os.path.dirname(dst_html_path))
            with codecs.open(dst_html_path, "wb+", "utf8") as fd:
                fd.write(output)

        yield {
            "basename": str(self.name),
            "name": dst_html_path,
            "targets": [dst_html_path],
            "actions": [(create_html, [])],
            'uptodate': [config_changed(kw)]
        }
