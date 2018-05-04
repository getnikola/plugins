# -*- coding: utf-8 -*-

# Copyright © 2017 Alexander Krimm.

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

"""Change navigation links below posts to next/previous post in category"""

from __future__ import unicode_literals
import blinker

from nikola.plugin_categories import SignalHandler


class CategoryNav(SignalHandler):
    """Change navigation links below posts to next/previous post in category"""

    name = "category"

    def _set_navlinks(self, site):
        # Needed to avoid strange errors during tests
        if site is not self.site:
            return
        # Update prev_post and next_post
        for lang, langposts in site.posts_per_classification['category'].items():
            for category, categoryposts in langposts.items():
                for i, p in enumerate(categoryposts[1:]):
                    p.next_post = categoryposts[i]
                for i, p in enumerate(categoryposts[:-1]):
                    p.prev_post = categoryposts[i + 1]
                categoryposts[0].next_post = None
                categoryposts[-1].prev_post = None

    def set_site(self, site):
        """Set site, which is a Nikola instance."""
        super(CategoryNav, self).set_site(site)
        # Add hook for after taxonomies_classifier has set site.posts_per_classification
        blinker.signal("taxonomies_classified").connect(self._set_navlinks)
