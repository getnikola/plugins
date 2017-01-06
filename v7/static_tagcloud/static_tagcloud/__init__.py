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

"""Render tag clouds."""

from nikola.plugin_categories import Task
from nikola import utils
from . import engine

import lxml.html
import natsort
import os

_LOGGER = utils.get_logger('render_static_tagcloud', utils.STDERR_HANDLER)


_DEFAULT_CONFIG = {
    # Tag cloud's name (used as CSS class). {0} will be replaced
    # by the language.
    'name': 'tc-{0}',
    # Filename for the HTML fragment. {0} will be replaced by the
    # language.
    'filename': 'tagcloud-{0}.inc.html',
    # The taxonomy type to obtain the classification ("tags")
    # from.
    'taxonomy_type': 'tag',
    # Filename for the CSS. {0} will be replaced by the language.
    'style_filename': 'assets/css/tagcloud-{0}.css',
    # Maximum number of levels to be generated
    'max_number_of_levels': 10,
    # Maximum number of tags in cloud. Negative values mean
    # that all tags will appear.
    'max_tags': -1,
    # Tags which appear less often than this number will be
    # ignored.
    'minimal_number_of_appearances': 1,
    # Colors defining a gradient out of which the tag font colors
    # are taken. The colors are specified as RGP triples with each
    # component being a floating point number between 0.0 and 1.0.
    'colors': ((0.4, 0.4, 0.4), (0.4, 0.4, 1.0), (1.0, 1.0, 1.0)),
    # Colors defining a gradient out of which the tag background
    # colors are taken.
    'background_colors': ((0.133, 0.133, 0.133), ),
    # Colors defining a gradient out of which the tag border colors
    # are taken.
    'border_colors': ((0.2, 0.2, 0.2), ),
    # Interval (min_value, max_value) for the font size
    'font_sizes': (6, 20),
    # If positive, will be multiplied by font size to yield the
    # CSS border radius and the vertical margin. (The horizontal
    # margin is set to zero.)
    'round_factor': 0.0,
}


class StaticTagCloud(Task):
    """Render tag clouds for various taxonomies."""

    name = "render_static_tagcloud"

    def _render_tagcloud_html(self, fn, tags, level_weights, config, lang, url_type):
        """Create tag cloud HTML fragment."""
        assert fn.startswith(self.site.config["OUTPUT_FOLDER"])
        # Create fragment
        html = engine.create_tag_cloud_html(config['name'], tags, level_weights)
        # Determine location (for link rewriting)
        url_part = fn[len(self.site.config["OUTPUT_FOLDER"]) + 1:]
        src = os.path.normpath(os.sep + url_part)
        src = "/".join(src.split(os.sep))
        # Rewrite links
        parser = lxml.html.HTMLParser(remove_blank_text=True)
        doc = lxml.html.fragment_fromstring(html, parser)
        self.site.rewrite_links(doc, src, lang, url_type)
        html = (doc.text or '').encode('utf-8') + b''.join([lxml.html.tostring(child, encoding='utf-8', method='html') for child in doc.iterchildren()])
        # Write result to disk
        with open(fn, "wb") as html_file:
            html_file.write(html)

    def _render_tagcloud_css(self, css_fn, tags, level_weights, config):
        """Create tag cloud CSS."""
        assert css_fn.startswith(self.site.config["OUTPUT_FOLDER"])

        css = engine.create_tag_cloud_css(config['name'], level_weights,
                                          colors=config['colors'],
                                          background_colors=config['background_colors'],
                                          border_colors=config['border_colors'],
                                          font_sizes=config['font_sizes'],
                                          round_factor=config['round_factor'])
        with open(css_fn, "wb") as css_file:
            css_file.write(css.encode('utf-8'))

    def _prepare_tagcloud(self, lang, config):
        """Create tag cloud task."""
        # Collect information
        fn = os.path.join(self.site.config['OUTPUT_FOLDER'], config['filename'])
        css_fn = os.path.join(self.site.config['OUTPUT_FOLDER'], config['style_filename'])
        taxonomy_type = config['taxonomy_type']
        posts_per_tag = self.site.posts_per_classification[taxonomy_type][lang]
        taxonomy = self.site.taxonomy_plugins[taxonomy_type]

        # Compose list of tags, their post count and links
        def acceptor(post):
            return True if self.site.config['SHOW_UNTRANSLATED_POSTS'] else post.is_translation_available(lang)

        tag_count_url_list = []
        for tag in natsort.humansorted(list(posts_per_tag.keys())):
            tag_count_url_list.append((
                taxonomy.get_classification_friendly_name(tag, lang),
                len([post for post in posts_per_tag[tag] if acceptor(post)]),
                self.site.link(taxonomy_type, tag, lang)
            ))

        # Get tag cloud data
        tags, level_weights = engine.create_tag_cloud_data(tag_count_url_list, max_number_of_levels=config['max_number_of_levels'], max_tags=config['max_tags'], minimal_number_of_appearances=config['minimal_number_of_appearances'])

        # Determine url type for rewriting. Must not be relative.
        url_type = self.site.config['URL_TYPE']
        if url_type == 'rel_path':
            url_type = 'full_path'

        # Create task for HTML fragment
        task = {
            'basename': self.name,
            'name': fn,
            'targets': [fn],
            'actions': [(self._render_tagcloud_html, [fn, tags, level_weights, config, lang, url_type])],
            'clean': True,
            'uptodate': [utils.config_changed({1: tags, 2: level_weights}, 'nikola.plugins.render_tagcloud:tags'), utils.config_changed(config, 'nikola.plugins.render_tagcloud:config')]
        }
        yield utils.apply_filters(task, self.site.config["FILTERS"])
        # Create task for CSS
        task = {
            'basename': self.name,
            'name': css_fn,
            'targets': [css_fn],
            'actions': [(self._render_tagcloud_css, [css_fn, tags, level_weights, config])],
            'clean': True,
            'uptodate': [utils.config_changed({1: tags, 2: level_weights}, 'nikola.plugins.render_tagcloud:tags'), utils.config_changed(config, 'nikola.plugins.render_tagcloud:config')]
        }
        yield utils.apply_filters(task, self.site.config["FILTERS"])

    def gen_tasks(self):
        """Generate tasks."""
        self.site.scan_posts()
        yield self.group_task()

        # Create tag clouds
        for name, config in self.site.config['RENDER_STATIC_TAGCLOUDS'].items():
            try:
                # Generic complete config
                generic_config = _DEFAULT_CONFIG.copy()
                generic_config.update(config)
                for lang in self.site.config['TRANSLATIONS'].keys():
                    # For a specific language, obtain the config by
                    # interpolation some strings with lang.
                    config = generic_config.copy()
                    config['name'] = config['name'].format(lang)
                    config['filename'] = config['filename'].format(lang)
                    config['style_filename'] = config['style_filename'].format(lang)
                    # Generate tasks
                    yield self._prepare_tagcloud(lang, config)
            except Exception as e:
                _LOGGER.error("Error occured while creating tag cloud '{0}': {1}".format(name, e))
                raise e
