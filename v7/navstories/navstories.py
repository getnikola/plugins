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
            # Which paths are navstories active for for lang?
            navstories_paths = ()
            if 'NAVSTORIES_PATHS' in site.config and lang in site.config['NAVSTORIES_PATHS']:
                navstories_paths = site.config['NAVSTORIES_PATHS'][lang]

            new = []
            newsub = {}
            for p in site.pages:
                permalink = p.permalink(lang)
                for s in navstories_paths:
                    if permalink.startswith('/' + s + '/'):
                        navpath = permalink[2 + len(s):].split('/') # Permalink format '/A/B/' for a story in s/A/B.rst
                        if  navpath[-1] == '':
                            del navpath[-1] # Also remove last element if empty
                        if lang in p.translated_to and not p.meta('hidefromnav'):
                            if len(navpath) <= 1:
                                new.append(p)
                            else:
                                # Add key if not exists
                                if not navpath[0] in newsub:
                                    newsub[navpath[0]] = []
                                # Add page to key
                                newsub[navpath[0]].append((p.permalink(lang), p.title(lang)))
            new_all = [(p.permalink(lang), p.title(lang)) for p in new]
            for k in sorted(newsub.keys()):
                new_all.append(tuple((tuple(newsub[k]), k)))
            new_entries = []
            navstories_mapping = ()
            if 'NAVSTORIES_MAPPING' in site.config and lang in site.config['NAVSTORIES_MAPPING']:
                navstories_mapping = site.config['NAVSTORIES_MAPPING'][lang]
            for sk, sv in navstories_mapping:
                for i in range(len(new_all)):
                    if sk == new_all[i][1]:
                        t = (new_all[i][0], sv)
                        new_entries.append(t)
                        del(new_all[i])
                        break
            new_entries.extend(new_all)
            new_entries = tuple(new_entries)
            old_entries = site.config['NAVIGATION_LINKS'].values[lang]
            # Get entries after navstories, defaults to none, else taken from NAVIGATION_LINKS_POST_NAVSTORIES, which have same format as NAVIGATION_LINKS in conf.py
            post_entries = ()
            if 'NAVIGATION_LINKS_POST_NAVSTORIES' in site.config:
                if lang in site.config['NAVIGATION_LINKS_POST_NAVSTORIES']:
                    post_entries = site.config['NAVIGATION_LINKS_POST_NAVSTORIES'][lang]
            site.config['NAVIGATION_LINKS'].values[lang] = old_entries + new_entries + post_entries
        super(NavStories, self).set_site(site)
