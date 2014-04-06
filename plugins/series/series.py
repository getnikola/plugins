# -*- coding: utf-8 -*-

# Copyright © 2014 Roberto Alsina

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
    makedirs,
    slugify,
)
from nikola.post import Post


class Plugin(Task):

    name = "series"

    def set_site(self, site):
        super(Plugin, self).set_site(site)
        site.register_path_handler('series', self.series_path)

        # Register helper functions in global context
        site.GLOBAL_CONTEXT['series_description'] = self.series_description

    def gen_tasks(self):
        self.kw = {
            'output_folder': self.site.config['OUTPUT_FOLDER'],
            'cache_folder': self.site.config['CACHE_FOLDER'],
            'default_lang': self.site.config['DEFAULT_LANG'],
            'translations': self.site.config['TRANSLATIONS'],
        }
        yield self.group_task()

        self.posts_per_series = defaultdict(list)
        for i in self.site.timeline:
            if i.meta('series'):
                self.posts_per_series[i.meta('series')].append(i)

        # Generate series/foo.html for each series "foo"
        for lang in self.kw['translations']:
            for series_name in self.posts_per_series.keys():

                output_name = os.path.join(
                    self.kw['output_folder'],
                    self.site.path('series', series_name, lang)
                )
                # FIXME: dependencies!
                yield {
                    'name': series_name,
                    'basename': 'series',
                    'actions': [(self.render_series_page, [series_name, output_name, lang])],
                    'uptodate': [False],
                }

        # This function will be called when the task is executed
        def render_series_index_page(series_list, output_name, lang):
            makedirs(os.path.dirname(output_name))
            context = {}
            context['items'] = [(name, self.site.link('series', name, lang)) for name in series_list]
            context['title'] = 'List of Series'  # FIXME: translations
            context['lang'] = lang
            self.site.render_template('list.tmpl', output_name, context)

        # Generate series/index.html with the list of all series
        for lang in self.kw['translations']:
            series_list = sorted(self.posts_per_series.keys())
            output_name = os.path.join(
                self.kw['output_folder'],
                self.site.path('series', None, lang)
            )
            # FIXME: dependencies!
            yield {
                'name': 'index',
                'basename': 'series',
                'actions': [(render_series_index_page, [series_list, output_name, lang])],
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
        if name is None:  # Series index
            return [_f for _f in [
                self.site.config['TRANSLATIONS'][lang],
                'series',
                self.site.config['INDEX_FILE']] if _f]

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

    def series_description(self, name, lang):
        "Return HTML describing a series and its posts, for using in templates."
        # FIXME: handle other extensions (sigh)
        series = self.parse_index(os.path.join('series', name + '.txt'))
        series.compile(lang)
        return series.text(lang)

    def render_series_page(self, name, output_name, lang):
        makedirs(os.path.dirname(output_name))
        context = {}
        # FIXME: handle other extensions (sigh)
        series = self.parse_index(os.path.join('series', name + '.txt'))
        # FIXME: render post in a task
        series.compile(lang)
        context['series'] = series
        # This is so we don't have to do a whole template, sorry
        context['post'] = series
        context['lang'] = lang
        context['title'] = series.title(lang)
        context['posts'] = self.posts_per_series[name]
        self.site.render_template('series.tmpl', output_name, context)
