# -*- coding: utf-8 -*-

# Copyright (c) 2024 Masin Wiedner

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

# inspired by
# * https://sd.ai/blog/2023-10-19/integrating-mastodon-and-ghost/
# * https://carlschwan.eu/2020/12/29/adding-comments-to-your-static-blog-with-mastodon/
# * https://berglyd.net/blog/2023/03/mastodon-comments/

from __future__ import unicode_literals
from nikola.plugin_categories import CommentSystem


class MastodonComments(CommentSystem):
    """Use Mastodon https://joinmastodon.org/ as a comment system"""
    def set_site(self, site):
        super(MastodonComments, self).set_site(site)
        site.template_hooks['extra_head'].append(
            '<link rel="stylesheet" href="/assets/css/mastodon.css" type="text/css">'
        )
