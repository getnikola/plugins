# -*- coding: utf-8 -*-

# Copyright © 2012-2014 Blake Winton <bwinton@latte.ca>.

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
from collections import defaultdict
import os

from nikola.plugin_categories import Task
from nikola.utils import config_changed


class SubIndexes(Task):
    """Render the indexes for each subdirectory in the blog."""

    name = "render_subindexes"

    def gen_tasks(self):
        self.site.scan_posts()
        yield self.group_task()

        kw = {
            "output_folder": self.site.config['OUTPUT_FOLDER'],
            "filters": self.site.config['FILTERS'],
            "index_file": self.site.config['INDEX_FILE'],
            "strip_indexes": self.site.config['STRIP_INDEXES'],
            "index_teasers": self.site.config['INDEX_TEASERS'],
        }
        template_name = "index.tmpl"
        for lang in self.site.config['TRANSLATIONS']:
            groups = defaultdict(list)
            for p in self.site.timeline:
                if p.is_post:
                    dirname = os.path.dirname(p.destination_path(lang))
                    dirname = [part for part in os.path.split(dirname) if part]
                    if dirname == ["."]:
                        continue
                    dirname.reverse()
                    part = ''
                    while len(dirname):
                        part = os.path.join(part, dirname.pop())
                        groups[part].append(p)

            for dirname, post_list in groups.items():
                context = {}
                context["items"] = []
                should_render = True
                output_name = os.path.join(kw['output_folder'], dirname, kw['index_file'])
                short_destination = os.path.join(dirname, kw['index_file'])
                link = short_destination.replace('\\', '/')
                index_len = len(kw['index_file'])
                if kw['strip_indexes'] and link[-(1 + index_len):] == '/' + kw['index_file']:
                    link = link[:-index_len]
                context["permalink"] = link

                for post in post_list:
                    # If there is an index.html pending to be created from
                    # a story, do not generate the STORY_INDEX
                    if post.destination_path(lang) == short_destination:
                        should_render = False
                    else:
                        context["items"].append((post.title(lang),
                                                 post.permalink(lang)))

                context['index_teasers'] = kw['index_teasers']
                context['pagekind'] = ['index']

                if should_render:
                    task = self.site.generic_post_list_renderer(lang, post_list,
                                                                output_name,
                                                                template_name,
                                                                kw['filters'],
                                                                context)
                    task_cfg = {1: task['uptodate'][0].config, 2: kw}
                    task['uptodate'] = [config_changed(task_cfg)]
                    task['basename'] = self.name
                    yield task
