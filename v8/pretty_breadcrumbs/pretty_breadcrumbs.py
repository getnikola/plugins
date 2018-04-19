# -*- coding: utf-8 -*-

# Copyright © 2018 Martin Michlmayr

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

import blinker
import os.path

from nikola.plugin_categories import SignalHandler
from nikola import utils


class PrettyBreadcrumbs(SignalHandler):

    def _set_pretty_crumbs(self, site):
        old_get_crumbs = utils.get_crumbs

        if 'PRETTY_BREADCRUMBS_TAG' in self.site.config:
            tag = self.site.config['PRETTY_BREADCRUMBS_TAG']
        else:
            tag = 'crumb'

        def pretty_get_crumbs(path, is_file=False, index_folder=None, lang=None):
            lang = lang if lang else utils.LocaleBorg().current_lang
            crumbs = old_get_crumbs(path, is_file=is_file, index_folder=index_folder, lang=lang)
            _crumbs = []
            for link, text in crumbs:
                if link == '#':
                    file = path
                else:
                    file = os.path.normpath(os.path.join(path, link))
                if not is_file:
                    file = os.path.join(file, self.site.config['INDEX_FILE'])
                if file in self.site.post_per_file:
                    post = self.site.post_per_file[file]
                    if tag in post.meta[lang]:
                        _crumbs.append([link, post.meta[lang][tag]])
                        continue
                _crumbs.append([link, text])
            return _crumbs

        # Set pretty_get_crumbs() as the new utils.get_crumbs()
        utils.get_crumbs = pretty_get_crumbs

    def set_site(self, site):
        """Set site, which is a Nikola instance."""
        super(PrettyBreadcrumbs, self).set_site(site)
        # Add hook for after post scanning
        blinker.signal("scanned").connect(self._set_pretty_crumbs)
