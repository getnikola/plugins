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
from nikola.utils import LOGGER


class Plugin(Task):

    name = "series"

    def gen_tasks(self):

        posts_per_series = defaultdict(list)
        for i in self.site.timeline:
            if i.meta('series'):
                posts_per_series[i.meta('series')].append(i)


        # This function will be called when the task is executed
        def render_series_page(name):
            LOGGER.notice(os.path.join('series', name + '.txt'))

        for series_name in posts_per_series.keys():
            yield {
                'basename': 'series',
                'actions': [(render_series_page, [series_name])],
                'uptodate': [False],
            }
