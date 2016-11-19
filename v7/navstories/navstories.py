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
from nikola.utils import LOGGER

import re

class NavStories(ConfigPlugin):
    """Add all stories to the navigation bar."""

    name = 'navstories'
    dates = {}

    conf_vars = ['TRANSLATIONS', 'NAVSTORIES_PATHS', 'NAVSTORIES_MAPPING', 'NAVIGATION_LINKS_POST_NAVSTORIES']

    # Indention for each level deeper in a submenu, than the highest level in that submenu
    # overwriiten by site.config['NAVSTORIES_SUBMENU_INDENTION'] if defined
    navstories_submenu_indention = '* '

    class NavNode():
        """
        Class containing parameters for a menu entry
        """

        navpath = []
        permalink = ''
        title = ''

        def __init__(self, navpath, permalink, title):
            self.navpath = navpath
            self.permalink = permalink
            self.title = title


    def map_to_menu(self, entries):
        """
        Map form list of pages going into menu to tuple of format as NAVIGATION_LINKS and NAVIGATION_LINKS_POST_NAVSTORIES
        List format:
        - List of "top level entry"
          - List
            - Top level Menu text, or None if auto-mapped, i.e. not in NAVSTORIES_MAPPING
            - List of pages in the top menu entry
              - List of:
                - navpath: List containing navigation hieracy (permalink without langinfo (initial /en/) and without the NAVSTORIES_PATHS (e.g. /pages/))
                - Permalink
                - Page title
        Example:
        [   [   'Menu text for nav',
                [   NavNode instance, # E.g.: .navpath=['nav'], .permalink='/pages/nav/', .title='nav/'
                    NavNode instance, # E.g.: .navpath=['nav', 'p2', 'a'], .permalink='/pages/nav/p2/a/', .title='Page 2a'
                    NavNode instance, # E.g.: .navpath=['nav', 'P2', 'b'], .permalink='/pages/nav/P2/b/', .title='Page 2b'
                    NavNode instance, # E.g.: .navpath=['nav', 'P2', 'a'], .permalink='/pages/nav/P2/a/', .title='Page 2a'
                    NavNode instance, # E.g.: .navpath=['nav', 'p2'],      .permalink='/pages/nav/p2/',   .title='Page 2',
                    NavNode instance, # E.g.: .navpath=['nav', 'p1'],      .permalink='/pages/nav/p1/',   .title='Side 1'
                ],
            [   'Menu text for A',
                [   NavNode instance, # E.g.: .navpath=['A', 'last'],      .permalink='/pages/A/last/',   .title='Page title for A/last'
                ],
            [   None,
                [   NavNode instance, # E.g.: .navpath=['B', 'cde'],       .permalink='/pages/B/cde/',    .title='Page title for B/cde'
            ],
        ]
        """
        ret = []
        for title, navnodes in entries:
            # Determine toplevel menu name
            # - If not None, use the name
            # - If None, use title of page if page with navpath length=1 exist, else navpath[0]
            if not title:
                # Default is 1th level of navpath
                title = navnodes[0].navpath[0]
                # Search for toplevel page (navpath length = 1)
                for n in navnodes:
                    if len(n.navpath) == 1:
                        title = n.title # Page Title
            if len(navnodes) == 1 and len(navnodes[0].navpath) == 1:
                # Only one menu item and it is not a subpage, let the item go direct to top level menu
                ret.append(tuple([navnodes[0].permalink, title]))
            else:
                sub = []
                # Find min/max depth in actual submenu
                min_depth = min(len(n.navpath) for n in navnodes)
                max_depth = max(len(n.navpath) for n in navnodes)
                # Map pages to submenu
                for n in sorted(navnodes, key=lambda n: n.permalink): # Sort by permalink in page list
                    prefix = self.navstories_submenu_indention * (len(n.navpath) - min_depth)
                    sub.append(tuple([n.permalink, prefix + n.title]))
                ret.append(tuple([tuple(sub), title]))
        return tuple(ret)


    def set_site(self, site):
        """
        Map navstories config to nav_config[*] as TranslatableSettings
        """

        # Read NAVSTORIES_SUBMENU_INDENTION and store in self.navstories_submenu_indention
        if 'NAVSTORIES_SUBMENU_INDENTION' in site.config:
            self.navstories_submenu_indention = site.config['NAVSTORIES_SUBMENU_INDENTION']

        nav_config = {}
        for i in self.conf_vars:
            # Read config variables in a try...except in case a varible is missing
            try:
                nav_config[i] = utils.TranslatableSetting(i, site.config[i], site.config['TRANSLATIONS'])
            except KeyError:
                # Initialize to "empty" in case config variable i is missng
                nav_config[i] = utils.TranslatableSetting(i, {}, site.config['TRANSLATIONS'])

        site.scan_posts()
        # NAVIGATION_LINKS is a TranslatableSetting, values is an actual dict
        for lang in site.config['NAVIGATION_LINKS'].values:
            # navstories config for lang
            nav_conf_lang = {}
            for i in self.conf_vars:
                 nav_conf_lang[i] = nav_config[i](lang)

            # Which paths are navstories active for current lang? - Must start and end with /
            paths = tuple(('/' + s.strip('/') + '/') for s in nav_conf_lang['NAVSTORIES_PATHS'])

            new_raw = {} # Unusorted (raw) new entries, deleted as mapped to new
            new = [] # Sorted entries as a list of top-level menu entries, later
            # Map site pages to new_raw structure
            for p in site.pages:
                # Generate mavpath (menu) based on permalink without language prefix
                # If TRANSLATION[DEFAULT_LANG] = '', then "permalink_nolang = p.permalink()" is ok
                permalink_nolang = re.sub(r'^/' + nav_conf_lang['TRANSLATIONS'].lstrip('./') + '/?', '/', p.permalink(lang))
                s_candidates = [s for s in paths if permalink_nolang.startswith(s)]
                if not s_candidates:
                    continue
                # get longest path
                s = max(s_candidates, key=len)
                # Strip off the longest path in paths
                navpath = permalink_nolang[len(s):].strip('/').split('/')
                if len(navpath) == 0:
                    # Should not happen that navpath is empty, but to prevent errors, and inform via a warning
                    LOGGER.warn("Page with permalink: '%s', title: '%s', not added to menu by navstories.\033[0m" % (p.permalink(lang), p.title(lang)))
                    continue
                if lang in p.translated_to and not p.meta('hidefromnav'):
                    # Add entry
                    if not navpath[0] in new_raw:
                        new_raw[navpath[0]] = []
                    new_raw[navpath[0]].append(self.NavNode(navpath, p.permalink(lang), p.title(lang)))

            # Map from new_raw to new, sorting by NAVSTORIES_MAPPING
            for map_key, map_txt in nav_conf_lang['NAVSTORIES_MAPPING']:
                # Loop over all new_raw entries, checking if it matches map_key; if match: add it and delete from new_raw
                if map_key in new_raw:
                    new.append([map_txt, new_raw[map_key]])
                    del(new_raw[map_key])
            # Add remaing new_raw entries which didn't match any map_key
            new.extend([[None, new_raw[_]] for _ in sorted(new_raw)])

            # Map to tuple
            new_entries = self.map_to_menu(new)
            old_entries = site.config['NAVIGATION_LINKS'](lang)
            # Update NAVIGATION_LINKS with navstories dynamically generated entries and NAVIGATION_LINKS_POST_NAVSTORIES entries
            site.config['NAVIGATION_LINKS'].values[lang] = old_entries + new_entries + nav_conf_lang['NAVIGATION_LINKS_POST_NAVSTORIES']
        super(NavStories, self).set_site(site)
