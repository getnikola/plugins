# -*- coding: utf-8 -*-

# Copyright © 2014–2015, Chris Warrick.

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
import io

from nikola.plugin_categories import Command
from nikola import utils


class UpgradeMetadata(Command):
    """Upgrade metadata from the old no-descriptions format to the new reST-esque format."""

    name = 'upgrade_metadata'
    doc_purpose = 'upgrade old-style metadata'
    cmd_options = [
        {
            'name': 'yes',
            'short': 'y',
            'long': 'yes',
            'type': bool,
            'default': False,
            'help': 'Proceed without confirmation',
        },
    ]
    fields = ('title', 'slug', 'date', 'tags', 'link', 'description', 'type')

    def _execute(self, options, args):
        L = utils.get_logger('upgrade_metadata', self.site.loghandlers)
        # scan posts
        self.site.scan_posts()
        flagged = []
        for post in self.site.timeline:
            if not post.newstylemeta:
                flagged.append(post)
        if flagged:
            if len(flagged) == 1:
                L.info('1 post contains old-style metadata:')
            else:
                L.info('{0} posts contain old-style metadata:'.format(len(flagged)))
            for post in flagged:
                L.info('    ' + post.metadata_path)
            if not options['yes']:
                yesno = utils.ask_yesno("Proceed with metadata upgrade?")
            if options['yes'] or yesno:
                for post in flagged:
                    with io.open(post.metadata_path, 'r', encoding='utf-8') as fh:
                        meta = fh.readlines()
                    with io.open(post.metadata_path, 'w', encoding='utf-8') as fh:
                        for k, v in zip(self.fields, meta):
                            fh.write('.. {0}: {1}'.format(k, v))
                L.info('{0} posts upgraded.'.format(len(flagged)))
            else:
                L.info('Metadata not upgraded.')
        else:
            L.info('No old-style metadata posts found.  No action is required.')
