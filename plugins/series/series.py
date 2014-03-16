# -*- coding: utf-8 -*-

# Copyright © 2012-2013 Roberto Alsina

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
from collections import defaultdict
import os

from nikola.plugin_categories import Task
from nikola.utils import (
    LOGGER,
    slugify,
)
from nikola.post import Post


class Plugin(Task):

    name = "series"

    def set_site(self, site):
        site.register_path_handler('series', self.series_path)
        return super(Plugin, self).set_site(site)

    def gen_tasks(self):
        self.kw = {
            'output_folder': self.site.config['OUTPUT_FOLDER'],
            'cache_folder': self.site.config['CACHE_FOLDER'],
            'default_lang': self.site.config['DEFAULT_LANG'],
            'translations': self.site.config['TRANSLATIONS'],
        }
        yield self.group_task()

        posts_per_series = defaultdict(list)
        for i in self.site.timeline:
            if i.meta('series'):
                posts_per_series[i.meta('series')].append(i)

        # This function will be called when the task is executed
        def render_series_page(name, output_name):
            LOGGER.warning(os.path.join('series', name + '.txt'))
            LOGGER.warning(output_name)

        for lang in self.kw['translations']:
            for series_name in posts_per_series.keys():
                output_name = os.path.join(
                    self.kw['output_folder'],
                    self.site.path('series', series_name, lang)
                )
                yield {
                    'name': series_name,
                    'basename': 'series',
                    'actions': [(render_series_page, [series_name, output_name])],
                    'uptodate': [False],
                }

    # FIXME this is 90% duplicated from the gallery plugin.
    # Time to refactor?
    def parse_index(self, post_path):
        """Returns a Post object from a foo.txt."""
        destination = os.path.join(
            self.kw["output_folder"],
            'series'
        )
        if os.path.isfile(post_path):
            post = Post(
                post_path,
                self.site.config,
                destination,
                False,
                self.site.MESSAGES,
                'story.tmpl',
                self.site.get_compiler(post_path)
            )
        else:
            post = None
        return post

    def series_path(self, name, lang):
        if self.site.config['PRETTY_URLS']:
            return [_f for _f in [
                self.site.config['TRANSLATIONS'][lang],
                'series',
                slugify(name),
                self.site.config['INDEX_FILE']] if _f]
        else:
            return [_f for _f in [
                self.site.config['TRANSLATIONS'][lang],
                'series',
                slugify(name) + ".html"] if _f]
