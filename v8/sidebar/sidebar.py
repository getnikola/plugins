# -*- coding: utf-8 -*-

# Copyright © 2014-2017 Felix Fontein
#
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

"""Render a sidebar to be included in all pages."""

from nikola.plugin_categories import Task
from nikola import utils

import natsort
import os
import os.path

_LOGGER = utils.get_logger('render_sidebar', utils.STDERR_HANDLER)


class RenderSidebar(Task):
    """Render a sidebar."""

    name = "render_sidebar"

    def set_site(self, site):
        """Set site."""
        super(RenderSidebar, self).set_site(site)

    def _build_post_list(self, lang, max_count):
        """Build list of the at most ``max_count`` most recent posts for the given language."""
        posts = list(self.site.posts)
        posts = sorted(posts, key=lambda post: post.date)
        posts.reverse()
        if not self.site.config['SHOW_UNTRANSLATED_POSTS']:
            posts = [post for post in posts if post.is_translation_available(lang)]
        return posts[:max_count]

    def _build_taxonomy_list_and_hierarchy(self, taxonomy_name, lang):
        """Build taxonomy list and hierarchy for the given taxnonmy name and language."""
        if taxonomy_name not in self.site.posts_per_classification or taxonomy_name not in self.site.taxonomy_plugins:
            return None, None
        posts_per_tag = self.site.posts_per_classification[taxonomy_name][lang]
        taxonomy = self.site.taxonomy_plugins[taxonomy_name]

        def acceptor(post):
            return True if self.site.config['SHOW_UNTRANSLATED_POSTS'] else post.is_translation_available(lang)

        # Build classification list
        classifications = [(taxonomy.get_classification_friendly_name(tag, lang, only_last_component=False), tag) for tag in posts_per_tag.keys()]
        if classifications:
            # Sort classifications
            classifications = natsort.humansorted(classifications)
            # Build items list
            result = list()
            for classification_name, classification in classifications:
                count = len([post for post in posts_per_tag[classification] if acceptor(post)])
                result.append((classification_name, count, self.site.link(taxonomy_name, classification, lang)))
            # Build hierarchy
            if taxonomy.has_hierarchy:
                # Special post-processing for archives: get rid of root and cut off tree at month level
                if taxonomy_name == 'archive':
                    root_list = self.site.hierarchy_per_classification[taxonomy_name][lang]
                    root_list = utils.clone_treenode(root_list[0]).children

                    def cut_depth(node, cutoff):
                        if cutoff <= 1:
                            node.children = []
                        else:
                            for node in node.children:
                                cut_depth(node, cutoff - 1)

                    def invert_order(node):
                        node.children.reverse()
                        for node in node.children:
                            invert_order(node)

                    # Make sure that days don't creep in
                    for node in root_list:
                        cut_depth(node, 2)
                        invert_order(node)
                    root_list.reverse()
                    flat_hierarchy = utils.flatten_tree_structure(root_list)
                else:
                    flat_hierarchy = self.site.flat_hierarchy_per_classification[taxonomy_name][lang]
            else:
                root_list = []
                for classification_name, classification in classifications:
                    node = utils.TreeNode(classification_name)
                    node.classification_name = classification
                    node.classification_path = taxonomy.extract_hierarchy(classification)
                    root_list.append(node)
                flat_hierarchy = utils.flatten_tree_structure(root_list)
            # Build flattened hierarchy list
            hierarchy = [(taxonomy.get_classification_friendly_name(node.classification_name, lang, only_last_component=False),
                          node.classification_name, node.classification_path,
                          self.site.link(taxonomy_name, node.classification_name, lang),
                          node.indent_levels, node.indent_change_before,
                          node.indent_change_after,
                          len(node.children),
                          len([post for post in posts_per_tag[node.classification_name] if acceptor(post)]))
                         for node in flat_hierarchy]
            return result, hierarchy
        else:
            return None, None

    def _prepare_sidebar(self, destination, lang, template):
        """Generates the sidebar task for the given language."""
        context = {}
        deps_dict = {}

        posts = self._build_post_list(lang, self.site.config.get("SIDEBAR_MAXIMUM_POST_COUNT ", 10))
        context['global_posts'] = posts
        deps_dict['global_posts'] = [(post.permalink(lang), post.title(lang), post.date) for post in posts]

        for taxonomy in self.site.taxonomy_plugins.keys():
            taxonomy_items, taxonomy_hierarchy = self._build_taxonomy_list_and_hierarchy(taxonomy, lang)
            context['global_{}_items'.format(taxonomy)] = taxonomy_items
            context['global_{}_hierarchy'.format(taxonomy)] = taxonomy_hierarchy
            deps_dict['global_{}_hierarchy'.format(taxonomy)] = taxonomy_hierarchy

        url_type = self.site.config['URL_TYPE']
        if url_type == 'rel_path':
            url_type = 'full_path'

        task = self.site.generic_renderer(lang, destination, template, self.site.config['FILTERS'], context=context, context_deps_remove=['global_posts'], post_deps_dict=deps_dict, url_type=url_type, is_fragment=True)
        task['basename'] = self.name
        yield task

    def gen_tasks(self):
        """Generate tasks."""
        self.site.scan_posts()
        yield self.group_task()

        for lang in self.site.config['TRANSLATIONS'].keys():
            destination = os.path.join(self.site.config['OUTPUT_FOLDER'], 'sidebar-{0}.inc'.format(lang))
            template = 'sidebar.tmpl'
            yield self._prepare_sidebar(destination, lang, template)
