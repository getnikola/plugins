# MIT License
#
# Copyright (c) [2024] [Diego Carrasco G.]
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import json
from nikola.plugin_categories import LateTask
from nikola import utils


class FlexSearchPlugin(LateTask):
    name = "flexsearch_plugin"

    def set_site(self, site):
        super(FlexSearchPlugin, self).set_site(site)
        self.site = site
        site.register_path_handler('search_index', self.search_index_path)

    def gen_tasks(self):
        """Generate the search index after all posts are processed."""
        self.site.scan_posts()
        yield self.group_task()

        output_path = self.site.config['OUTPUT_FOLDER']
        index_file_path = os.path.join(output_path, 'search_index.json')

        def build_index():
            """Build the entire search index from scratch, including both posts and pages."""
            index = {}

            # Get configuration for what content to include
            # Default to True for backward compatibility
            index_posts = self.site.config.get('FLEXSEARCH_INDEX_POSTS', True)
            index_pages = self.site.config.get('FLEXSEARCH_INDEX_PAGES', False)
            index_drafts = self.site.config.get('FLEXSEARCH_INDEX_DRAFTS', False)

            for item in self.site.timeline:
                # Skip draft items unless configured to include them
                if item.is_draft and not index_drafts:
                    continue

                # Include posts if configured
                if item.is_post and index_posts:
                    index[item.meta('slug')] = {
                        'title': item.title(),
                        # 'content': item.text(strip_html=True),
                        'tags': item.meta('tags'),
                        'url': item.permalink(),
                        'type': 'post'
                    }
                # Include pages if configured
                elif not item.is_post and index_pages:
                    index[item.meta('slug')] = {
                        'title': item.title(),
                        # 'content': item.text(strip_html=True),
                        'tags': item.meta('tags'),
                        'url': item.permalink(),
                        'type': 'page'
                    }

            with open(index_file_path, 'w', encoding='utf-8') as f:
                json.dump(index, f, ensure_ascii=False)

        task = {
            'basename': self.name,
            'name': 'all_posts',
            'actions': [build_index],
            'targets': [index_file_path],
            'uptodate': [utils.config_changed({1: self.site.GLOBAL_CONTEXT})],
            'clean': True,
        }
        yield task

    def search_index_path(self, name, lang):
        return [os.path.join(self.site.config['BASE_URL'], 'search_index.json'), None]
