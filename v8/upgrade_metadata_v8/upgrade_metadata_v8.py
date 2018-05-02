# -*- coding: utf-8 -*-

# Copyright © 2014–2015, Chris Warrick.
# Copyright © 2018, Felix Fontein.

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
import os
import nikola.post
from nikola.plugin_categories import Command
from nikola import utils


class UpgradeMetadata(Command):
    """Convert special tags (draft, private, mathjax) to status and has_math metadata."""

    name = 'upgrade_metadata_v8'
    doc_purpose = 'Convert special tags (draft, private, mathjax) to metadata'
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

    def _execute(self, options, args):
        L = utils.get_logger('upgrade_metadata_v8', utils.STDERR_HANDLER)

        # scan posts
        self.site.scan_posts()
        flagged = []
        for post in self.site.timeline:
            if post.has_oldstyle_metadata_tags:
                flagged.append(post)
        if flagged:
            if len(flagged) == 1:
                L.info('1 post (and/or its translations) contains old-style metadata:')
            else:
                L.info('{0} posts (and/or their translations) contain old-style metadata:'.format(len(flagged)))
            for post in flagged:
                L.info('    ' + post.metadata_path)
            if not options['yes']:
                yesno = utils.ask_yesno("Proceed with metadata upgrade?")
            if options['yes'] or yesno:
                for post in flagged:
                    for lang in self.site.config['TRANSLATIONS'].keys():
                        if lang == post.default_lang:
                            fname = post.metadata_path
                        else:
                            meta_path = os.path.splitext(post.source_path)[0] + '.meta'
                            fname = utils.get_translation_candidate(post.config, meta_path, lang)

                        if os.path.exists(fname):
                            with io.open(fname, 'r', encoding='utf-8') as fh:
                                meta = fh.readlines()

                            if not meta[min(1, len(meta) - 1)].startswith('.. '):
                                # check if we’re dealing with old style metadata
                                with io.open(fname, 'w', encoding='utf-8') as fh:
                                    for k, v in zip(self.fields, meta):
                                        fh.write('.. {0}: {1}'.format(k, v))
                                L.debug(fname)

                L.info('{0} posts upgraded.'.format(len(flagged)))
            else:
                L.info('Metadata not upgraded.')
        else:
            L.info('No posts found with special tags.  No action is required.')
            L.info('You can safely set the USE_TAG_METADATA and the WARN_ABOUT_TAG_METADATA settings to False.')
