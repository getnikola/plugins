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
from nikola import utils


class NavStories(ConfigPlugin):
    """Add all stories to the navigation bar."""

    name = 'navstories'
    dates = {}

    conf_vars = ['NAVSTORIES_PATHS', 'NAVSTORIES_MAPPING', 'NAVIGATION_LINKS_POST_NAVSTORIES']

    def set_site(self, site):
        # Map navstories config to nav_config[*] as TranslatableSettings
        nav_config = {}
        for i in self.conf_vars:
            try:
                nav_config[i] = ()
                nav_config[i] = site.config[i]
                nav_config[i] = utils.TranslatableSetting(i, site.config[i], site.config['TRANSLATIONS'])
            except KeyError:
                pass

        site.scan_posts()
        # NAVIGATION_LINKS is a TranslatableSetting, values is an actual dict
        for lang in site.config['NAVIGATION_LINKS'].values:
            # navstories config for lang
            nav_conf_lang = {}
            for i in self.conf_vars:
                 nav_conf_lang[i] = nav_config[i].values[lang]

            # Which paths are navstories active for current lang? - Must start and end with /
            paths = tuple(('/' + s.strip('/') + '/') for s in nav_conf_lang['NAVSTORIES_PATHS'])

            new = []
            newsub = {}
            for p in site.pages:
                permalink = p.permalink()
                s_candidates = [s for s in paths if permalink.startswith(s)]
                if not s_candidates:
                    continue
                # get longest path
                s = max(s_candidates, key=len)
                # Strip off the longest path in paths
                navpath = permalink[len(s):].split('/')
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
                        newsub[navpath[0]].append((p.permalink(), p.title(lang)))
            # Change new to be list of tuples(permalink, title)
            new = [(p.permalink(), p.title(lang)) for p in new]
            # Add content of newsub (containg menu entries and submenus) to new (which was pages without subpages)
            for k in sorted(newsub.keys()):
                # Add submenu entries sorted by permalink
                new.append(tuple((tuple(sorted(newsub[k])), k)))
            new_entries = []
            for map_key, map_txt in nav_conf_lang['NAVSTORIES_MAPPING']:
                # Loop over all new entries, checking if it matches map_key; if match: add it and delete from new
                for i in range(len(new)):
                    if map_key == new[i][1]:
                        t = (new[i][0], map_txt)
                        new_entries.append(t)
                        del(new[i])
                        break
            # Add remaing new entries which didn't match any map_key
            new_entries.extend(new)
            new_entries = tuple(new_entries)
            old_entries = site.config['NAVIGATION_LINKS'].values[lang]
            # Update NAVIGATION_LINKS with navstories dynamically generated entries and NAVIGATION_LINKS_POST_NAVSTORIES entries
            site.config['NAVIGATION_LINKS'].values[lang] = old_entries + new_entries + nav_conf_lang['NAVIGATION_LINKS_POST_NAVSTORIES']
        super(NavStories, self).set_site(site)
