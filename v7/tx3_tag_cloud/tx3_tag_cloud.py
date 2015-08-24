# -*- coding: utf-8 -*-

# Copyright © 2015 Manuel Kaufmann

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

import os
import json

from nikola import utils
from nikola.plugin_categories import Task


class Tx3TagCloud(Task):

    """Render the tags to be used by tx3TagCloud plugin."""

    name = "tx3_tag_cloud"

    def set_site(self, site):
        """Set Nikola site."""
        return super(Tx3TagCloud, self).set_site(site)

    def gen_tasks(self):
        """Render the tag pages and feeds."""
        kw = {
            "output_folder": self.site.config['OUTPUT_FOLDER'],
            'tag_path': self.site.config['TAG_PATH'],
            "tag_pages_are_indexes": self.site.config['TAG_PAGES_ARE_INDEXES'],
            'category_path': self.site.config['CATEGORY_PATH'],
            'category_prefix': self.site.config['CATEGORY_PREFIX'],
            "taglist_minimum_post_count": self.site.config['TAGLIST_MINIMUM_POSTS'],
            "pretty_urls": self.site.config['PRETTY_URLS'],
            "strip_indexes": self.site.config['STRIP_INDEXES'],
        }
        self.site.scan_posts()

        # Copy all the assets to the right places
        asset_folder = os.path.join(os.path.dirname(__file__), "files")
        for task in utils.copy_tree(asset_folder, kw["output_folder"]):
            task["basename"] = str(self.name)
            yield task

        # Tag cloud json file
        tag_cloud_data = {}
        for tag, posts in self.site.posts_per_tag.items():
            if tag in self.site.config['HIDDEN_TAGS'] or len(posts) < kw['taglist_minimum_post_count']:
                continue
            tag_cloud_data[tag] = [len(posts), self.site.link(
                'tag', tag, self.site.config['DEFAULT_LANG'])]
        output_name = os.path.join(kw['output_folder'],
                                   'assets', 'js', 'tx3_tag_cloud.json')

        def write_tag_data(data):
            """Write tag data into JSON file, for use in tag clouds."""
            utils.makedirs(os.path.dirname(output_name))
            with open(output_name, 'w+') as fd:
                json.dump(data, fd)

        task = {
            'basename': str(self.name),
            'name': str(output_name)
        }

        task['uptodate'] = [utils.config_changed(tag_cloud_data, 'nikola.plugins.task.tags:tagdata')]
        task['targets'] = [output_name]
        task['actions'] = [(write_tag_data, [tag_cloud_data])]
        task['clean'] = True
        yield task
