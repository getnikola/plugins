# -*- coding: utf-8 -*-

# Copyright © 2012-2016 Roberto Alsina and others.

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

"""Generate Podcast Specific RSS Feeds"""

import os
import mimetypes
try:
    from urlparse import urljoin
except ImportError:
    from urllib.parse import urljoin  # NOQA
from nikola import utils
from nikola.plugin_categories import TaskMultiplier


class GeneratePodcastRSS(TaskMultiplier):
    """Generate Podcast Specific RSS feeds."""

    name = "gen_pod_rss"

    def process(self, task, prefix):

        """Process Tasks"""
        if not self.site.config['PODCAST_RSS']:
            return []
        if task.get('name') is None:
            return []

        utils.LOGGER.warn("process called for Gen Pod Feed")
        utils.LOGGER.warn(self.site.path_handlers)
        # utils.LOGGER.warn(self.site.config['TRANSLATIONS'])
        # utils.LOGGER.warn("Targets: %s", task.get('targets', []))
        kw = {
            "translations": self.site.config["TRANSLATIONS"],
            "filters": self.site.config["FILTERS"],
            "blog_title": self.site.config["BLOG_TITLE"],
            "site_url": self.site.config["SITE_URL"],
            "blog_description": self.site.config["BLOG_DESCRIPTION"],
            "output_folder": self.site.config["OUTPUT_FOLDER"],
            "feed_teasers": self.site.config["FEED_TEASERS"],
            "feed_plain": self.site.config["FEED_PLAIN"],
            "show_untranslated_posts": self.site.config['SHOW_UNTRANSLATED_POSTS'],
            "feed_length": self.site.config['FEED_LENGTH'],
            "feed_read_more_link": self.site.config["FEED_READ_MORE_LINK"],
            "feed_links_append_query": self.site.config["FEED_LINKS_APPEND_QUERY"],
        }
        utils.LOGGER.warn("KW Set")

        feed_task = {
            'file_dep': [],
            'targets': [],
            'actions': [],
            'uptodate': [],
            'basename': '{0}_podcast_rss'.format(prefix),
            'name': task.get('name').split(":", 1)[-1],
            'task_dep': ['render_site'],
            'clean': True
        }
        utils.LOGGER.warn("Feed Task Set")

        deps = []
        deps_uptodate = []
        for feed in self.site.config['PODCAST_FEEDS']:
            feed_name = "rss_" + feed
            utils.LOGGER.warn("Adding action for: %s", feed)
            for lang in kw['translations']:
                utils.LOGGER.warn("Doing work for: %s", lang)
                utils.LOGGER.warn("output folder: %s", kw['output_folder'])
                utils.LOGGER.warn("output path: %s", self.site.path(feed_name, None, lang))
                output_name = os.path.join(kw['output_folder'], self.site.path(feed_name, None, lang))
                utils.LOGGER.warn("Setting Output to: %s", output_name)

                if kw["show_untranslated_posts"]:
                    posts = self.site.posts[:kw['feed_length']]
                else:
                    posts = [x for x in self.site.posts if x.is_translation_available(lang)][:kw['feed_length']]
                for post in posts:
                    deps += post.deps(lang)
                    deps_uptodate += post.deps_uptodate(lang)

                feed_url = urljoin(self.site.config['BASE_URL'], self.site.link("rss_" + feed, None, lang).lstrip('/'))

                feed_task['actions'].append((utils.generic_rss_renderer,
                                            (lang, kw["blog_title"](lang), kw["site_url"],
                                                kw["blog_description"](lang), posts, output_name,
                                                kw["feed_teasers"], kw["feed_plain"], kw['feed_length'], feed_url,
                                                self._enclosure, kw["feed_links_append_query"])))
                feed_task['targets'].append(output_name)
        feed_task['uptodate'] = deps_uptodate
        feed_task['file_dep'] = deps
        return [feed_task]

    def _enclosure(self, post, feed, lang):
        enclosure = post.meta(feed + "_enclosure", lang)
        if enclosure:
            try:
                length = int(post.meta(feed + '_enclosure_length', lang) or 0)
            except KeyError:
                length = 0
            except ValueError:
                utils.LOGGER.warn("Invalid enclosure length for post {0}".format(post.source_path))
                length = 0
            url = enclosure
            mime = mimetypes.guess_type(url)[0]
            return url, length, mime

    """
    Honestly, does this need to be a method? can I make it some kind of lambda?
    """
    def _rss_path(self, name, lang):
        """A link to the RSS feed path.

        Example:

        link://rss => /blog/rss_ogg.xml
        """
        utils.LOGGER.warn("name: %s", name)
        res = []
        for feed in self.site.config['PODCAST_FEEDS']:
            res.append([_f for _f in [self.site.config['TRANSLATIONS'][lang],
                                      self.site.config['RSS_PATH'], 
                                      'rss_' + feed + '.xml'] 
                        if _f])
        return res

    def set_site(self, site):
        """Set Nikola site."""
        for feed in site.config['PODCAST_FEEDS']:
            site.register_path_handler('rss_' + feed, self._rss_path)
        return super(GeneratePodcastRSS, self).set_site(site)
