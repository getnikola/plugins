# -*- coding: utf-8 -*-

# Copyright © 2016 Felix Fontein and Nikola contributors

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

"""The default post scanner."""

from __future__ import unicode_literals, print_function
import glob
import os
import sys

from nikola.plugin_categories import PostScanner
from nikola import utils
from nikola.post import Post

LOGGER = utils.get_logger('hierarchical_pages', utils.STDERR_HANDLER)


def _spread(input, translations, default_language):
    if isinstance(input, dict):
        if default_language in input:
            def_value = input[default_language]
        else:
            def_value = input[list(input.keys())[0]]
        return {lang: input[lang] if lang in input else def_value for lang in translations.keys()}
    else:
        return {lang: input for lang in translations.keys()}


class Node(object):
    def __init__(self, name=None, slugs=None):
        self.name = name
        self.children = {}
        self.slugs = slugs
        self.post_source = None

    def __repr__(self):
        return "Node({}; {}; {})".format(self.post_source, self.slugs, self.children)


class HierarchicalPages(PostScanner):
    """Scan posts in the site."""

    name = "hierarchical_pages"

    def scan(self):
        """Create list of posts from HIERARCHICAL_PAGES options."""
        seen = set([])
        if not self.site.quiet:
            print("Scanning hierarchical pages", end='', file=sys.stderr)

        timeline = []

        for wildcard, destination, template_name in self.site.config.get('HIERARCHICAL_PAGES', []):
            if not self.site.quiet:
                print(".", end='', file=sys.stderr)
            root = Node(slugs=_spread(destination, self.site.config['TRANSLATIONS'], self.site.config['DEFAULT_LANG']))
            dirname = os.path.dirname(wildcard)
            for dirpath, _, _ in os.walk(dirname, followlinks=True):
                # Get all the untranslated paths
                dir_glob = os.path.join(dirpath, os.path.basename(wildcard))  # posts/foo/*.rst
                untranslated = glob.glob(dir_glob)
                # And now get all the translated paths
                translated = set([])
                for lang in self.site.config['TRANSLATIONS'].keys():
                    if lang == self.site.config['DEFAULT_LANG']:
                        continue
                    lang_glob = utils.get_translation_candidate(self.site.config, dir_glob, lang)  # posts/foo/*.LANG.rst
                    translated = translated.union(set(glob.glob(lang_glob)))
                # untranslated globs like *.rst often match translated paths too, so remove them
                # and ensure x.rst is not in the translated set
                untranslated = set(untranslated) - translated

                # also remove from translated paths that are translations of
                # paths in untranslated_list, so x.es.rst is not in the untranslated set
                for p in untranslated:
                    translated = translated - set([utils.get_translation_candidate(self.site.config, p, l) for l in self.site.config['TRANSLATIONS'].keys()])

                full_list = list(translated) + list(untranslated)
                # We eliminate from the list the files inside any .ipynb folder
                full_list = [p for p in full_list
                             if not any([x.startswith('.')
                                         for x in p.split(os.sep)])]

                for base_path in full_list:
                    if base_path in seen:
                        continue
                    else:
                        seen.add(base_path)
                    # Extract path
                    path = utils.os_path_split(os.path.relpath(base_path, dirname))
                    path[-1] = os.path.splitext(path[-1])[0]
                    if path[-1] == 'index':
                        path = path[:-1]
                    # Find node
                    node = root
                    for path_elt in path:
                        if path_elt not in node.children:
                            node.children[path_elt] = Node(path_elt)
                        node = node.children[path_elt]
                    node.post_source = base_path

            # Add posts
            def crawl(node, destinations_so_far, root=True):
                if node.post_source is not None:
                    try:
                        post = Post(
                            node.post_source,
                            self.site.config,
                            '',
                            False,
                            self.site.MESSAGES,
                            template_name,
                            self.site.get_compiler(node.post_source),
                            destination_base=utils.TranslatableSetting('destinations', destinations_so_far, self.site.config['TRANSLATIONS']),
                            metadata_extractors_by=self.site.metadata_extractors_by
                        )
                        timeline.append(post)
                    except Exception as err:
                        LOGGER.error('Error reading post {}'.format(base_path))
                        raise err
                    # Compute slugs
                    slugs = {}
                    for lang in self.site.config['TRANSLATIONS']:
                        slug = post.meta('slug', lang=lang)
                        if slug:
                            slugs[lang] = slug
                    if not slugs:
                        slugs[self.site.config['DEFAULT_LANG']] = node.name
                    node.slugs = _spread(slugs, self.site.config['TRANSLATIONS'], self.site.config['DEFAULT_LANG'])
                # Update destinations_so_far
                if not root:
                    if node.slugs is not None:
                        destinations_so_far = {lang: os.path.join(dest, node.slugs[lang]) for lang, dest in destinations_so_far.items()}
                    else:
                        destinations_so_far = {lang: os.path.join(dest, node.name) for lang, dest in destinations_so_far.items()}
                for p, n in node.children.items():
                    crawl(n, destinations_so_far, root=False)

            crawl(root, root.slugs)

        return timeline

    def supported_extensions(self):
        """Return a list of supported file extensions, or None if such a list isn't known beforehand."""
        return list({os.path.splitext(x[0])[1] for x in self.site.config.get('HIERARCHICAL_PAGES', [])})
