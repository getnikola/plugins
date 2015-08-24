# -*- coding: utf-8 -*-

# Copyright © 2014 Chris Warrick and others.

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
from nikola.plugin_categories import ConfigPlugin


class NavStories(ConfigPlugin):
    """Add all stories to the navigation bar."""

    name = 'navstories'
    dates = {}

    def set_site(self, site):
        site.scan_posts()
        # NAVIGATION_LINKS is a TranslatableSetting, values is an actual dict
        for lang in site.config['NAVIGATION_LINKS'].values:
            new = []
            for p in site.pages:
                if lang in p.translated_to and not p.meta('hidefromnav'):
                    new.append(p)
            new_entries = tuple(sorted([(p.permalink(lang), p.title(lang)) for p in new]))

            old_entries = site.config['NAVIGATION_LINKS'].values[lang]
            site.config['NAVIGATION_LINKS'].values[lang] = old_entries + new_entries
        super(NavStories, self).set_site(site)
