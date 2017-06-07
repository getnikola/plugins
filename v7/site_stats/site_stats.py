"""A Nikola plugin to compute and add site statistics to global context."""

import logbook
from nikola.plugin_categories import ConfigPlugin
from nikola import utils


LOGGER = utils.get_logger("site_stats", utils.STDERR_HANDLER)


class SiteStats(ConfigPlugin):
    """Add site statistics to global context"""

    name = "site_stats"
    debug = False

    def set_site(self, site):
        site.scan_posts()
        if self.debug:
            for handler in LOGGER.handlers:
                handler.level = logbook.DEBUG
        self.set_post_count(site)
        self.set_category_count(site)
        self.set_tag_count(site)
        super(SiteStats, self).set_site(site)

    def set_post_count(self, site):
        post_count = len(site.posts)
        LOGGER.debug('post_count: %s' % post_count)
        site.GLOBAL_CONTEXT['post_count'] = post_count

    def set_tag_count(self, site):
        tag_count = len(site.posts_per_tag)
        LOGGER.debug('tag_count: %s' % tag_count)
        site.GLOBAL_CONTEXT['tag_count'] = tag_count

    def set_category_count(self, site):
        category_count = len(site.posts_per_category)
        LOGGER.debug('category_count: %s' % category_count)
        site.GLOBAL_CONTEXT['category_count'] = category_count
