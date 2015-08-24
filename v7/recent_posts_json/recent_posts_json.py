# -*- coding: utf-8 -*-

# Copyright © 2012-2015 Roberto Alsina and others.

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
import io
import json
import time
try:
    from urlparse import urljoin
except ImportError:
    from urllib.parse import urljoin  # NOQA

from nikola import utils
from nikola.plugin_categories import Task


class RecentPostsJon(Task):
    """Generate JSON with recent posts."""

    name = "recent_posts_json"

    def set_site(self, site):
        site.register_path_handler("recent_posts_json", self.json_path)
        return super(RecentPostsJon, self).set_site(site)

    def gen_tasks(self):
        """Generate RSS feeds."""
        kw = {
            "output_folder": self.site.config["OUTPUT_FOLDER"],
            "filters": self.site.config["FILTERS"],
            "index_file": self.site.config["INDEX_FILE"],
            "translations": self.site.config["TRANSLATIONS"],
            "show_untranslated_posts": self.site.config["SHOW_UNTRANSLATED_POSTS"],
            "site_url": self.site.config["SITE_URL"],
            "base_url": self.site.config["BASE_URL"],
            "json_posts_length": self.site.config["RECENT_POSTS_JSON_LENGTH"] if "RECENT_POSTS_JSON_LENGTH" in self.site.config else self.site.config["INDEX_DISPLAY_POST_COUNT"],
            "json_descriptions": self.site.config["RECENT_POSTS_JSON_DESCRIPTION"] if "RECENT_POSTS_JSON_DESCRIPTION" in self.site.config else False,
            "json_previewimage": self.site.conf["RECENT_POSTS_JSON_PREVIEWIMAGE"] if "RECENT_POSTS_JSON_PREVIEWIMAGE" in self.site.config else False,
        }
        self.site.scan_posts()
        yield self.group_task()
        for lang in kw["translations"]:
            output_path = os.path.join(kw["output_folder"],
                                       self.site.path("recent_posts_json", None, lang))
            deps = []
            deps_uptodate = []
            if kw["show_untranslated_posts"]:
                posts = self.site.posts[:kw["json_posts_length"]]
            else:
                posts = [x for x in self.site.posts if x.is_translation_available(lang)][:kw["json_posts_length"]]
            for post in posts:
                deps += post.deps(lang)
                deps_uptodate += post.deps_uptodate(lang)
            task = {
                "basename": "recent_posts_json",
                "name": os.path.normpath(output_path),
                "file_dep": deps,
                "targets": [output_path],
                "actions": [(self.make_json,
                            (posts, kw["json_descriptions"], kw["json_previewimage"], output_path))],
                "task_dep": ["render_posts"],
                "clean": True,
                "uptodate": [utils.config_changed(kw, "nikola.plugins.task.recent_pots_json")] + deps_uptodate,
            }
            yield utils.apply_filters(task, kw["filters"])

    def make_json(self, posts, descriptions, previewimage, output_path):
        recent_posts = []
        for post in posts:
            date = int(time.mktime(post.date.timetuple()) * 1000)  # JavaScript Date
            link = post.permalink(absolute=False)
            title = post.title()
            entry = {"date": date,
                     "loc": link,
                     "title": title}
            if descriptions:
                entry.update({["desc"]: post.description()})
            if previewimage:
                entry.update({["img"]: post.previewimage()})
            recent_posts.append(entry)
        data = json.dumps(recent_posts, indent=2, sort_keys=True)
        with io.open(output_path, "w+", encoding="utf8") as outf:
            outf.write(data)

    def json_path(self, name, lang):
        return [_f for _f in [self.site.config["TRANSLATIONS"][lang],
                              os.path.splitext(self.site.config["INDEX_FILE"])[0] + ".json"] if _f]
