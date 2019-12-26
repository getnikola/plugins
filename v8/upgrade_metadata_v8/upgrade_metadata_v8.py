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
import sys
from nikola.plugin_categories import Command
from nikola import utils


class UpgradeMetadata(Command):
    """Convert special tags (draft, private, mathjax) to status and has_math metadata. Also removes sections."""

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
        L = utils.get_logger('upgrade_metadata_v8')

        if not self.site.config['USE_TAG_METADATA']:
            L.error('This plugin can only be used if USE_TAG_METADATA is set to True.')
            sys.exit(-1)
        self.site.config['WARN_ABOUT_TAG_METADATA'] = False

        # scan posts
        self.site.scan_posts()
        flagged = []
        for post in self.site.timeline:
            flag = False
            if post.has_oldstyle_metadata_tags:
                flag = True
            for lang in self.site.config['TRANSLATIONS'].keys():
                if 'section' in post.meta[lang]:
                    flag = True
            if flag:
                flagged.append(post)
        if flagged:
            if len(flagged) == 1:
                L.info('1 post (and/or its translations) contains old-style metadata or has section metadata:')
            else:
                L.info('{0} posts (and/or their translations) contain old-style metadata or have section metadata:'.format(len(flagged)))
            for post in flagged:
                L.info('    ' + (post.metadata_path if post.is_two_file else post.source_path))
            L.warn('Please make a backup before running this plugin. It might eat your data.')
            if not options['yes']:
                yesno = utils.ask_yesno("Proceed with metadata upgrade?")
            if options['yes'] or yesno:
                number_converted = 0
                number_converted_partial = 0
                for post in flagged:
                    converted = False
                    fully_converted = True
                    for lang in self.site.config['TRANSLATIONS'].keys():
                        # Get file names and extractor
                        extractor = post.used_extractor[lang]
                        is_two_file = post.is_two_file
                        if lang == post.default_lang:
                            fname = post.metadata_path if is_two_file else post.source_path
                        else:
                            meta_path = os.path.splitext(post.source_path)[0] + '.meta' if is_two_file else post.source_path
                            fname = utils.get_translation_candidate(post.config, meta_path, lang)

                        # We don't handle compilers which extract metadata for now
                        if post.compiler is extractor:
                            L.warn('Cannot convert {0} (language {1}), as metadata was extracted by compiler.'.format(fname, lang))
                            fully_converted = False
                            continue

                        # Read metadata and text from post file
                        if not os.path.exists(fname):
                            L.debug("File {0} does not exist, skipping.".format(fname))
                            continue

                        with io.open(fname, "r", encoding="utf-8-sig") as meta_file:
                            source_text = meta_file.read()
                        if not is_two_file:
                            _, content_str = extractor.split_metadata_from_text(source_text)
                        meta = extractor.extract_text(source_text)

                        # Consider metadata mappings
                        sources = {}
                        for m in ('tags', 'status', 'has_math', 'section', 'category'):
                            sources[m] = m
                        for foreign, ours in self.site.config.get('METADATA_MAPPING', {}).get(extractor.map_from, {}).items():
                            if ours in sources:
                                sources[ours] = foreign
                        for meta_key, hook in self.site.config.get('METADATA_VALUE_MAPPING', {}).get(extractor.map_from, {}).items():
                            if meta_key in sources.values():
                                L.warn('Cannot convert {0} (language {1}): a metadata value mapping is defined for "{2}"!'.format(fname, lang, meta_key))

                        # Update metadata
                        updated = False
                        tags = meta.get(sources['tags'], [])
                        tags_are_string = False
                        if not isinstance(tags, list):
                            tags_are_string = True
                            tags = [tag.strip() for tag in tags.split(',') if tag.strip()]

                        if 'draft' in [_.lower() for _ in tags]:
                            tags.remove('draft')
                            meta[sources['status']] = 'draft'
                            updated = True

                        if 'private' in tags:
                            tags.remove('private')
                            meta[sources['status']] = 'private'
                            updated = True

                        if 'mathjax' in tags:
                            tags.remove('mathjax')
                            meta[sources['has_math']] = 'yes'
                            updated = True

                        if meta.get(sources['section']):
                            if meta.get(sources['category']):
                                L.warn('Cannot completely {0} (language {1}): both section and category are specified. Please determine the correct category to use yourself!'.format(fname, lang))
                                fully_converted = False
                            else:
                                meta[sources['category']] = meta[sources['section']]
                                del meta[sources['section']]
                                updated = True

                        if tags_are_string:
                            meta[sources['tags']] = ', '.join(tags)

                        if not updated:
                            # Nothing to do (but successful)!
                            converted = True
                            continue

                        # Recombine metadata with post text if necessary, and write back to file
                        meta_str = utils.write_metadata(meta, metadata_format=extractor.name, compiler=post.compiler,
                                                        comment_wrap=(post.compiler.name != 'rest'), site=self.site)
                        final_str = meta_str if is_two_file else (meta_str + content_str)

                        with io.open(fname, "w", encoding="utf-8") as meta_file:
                            meta_file.write(final_str)
                            converted = True

                    if converted:
                        if fully_converted:
                            number_converted += 1
                        else:
                            number_converted_partial += 1

                L.info('{0} out of {2} posts upgraded; {1} only converted partially '
                       '(see above output).'.format(number_converted + number_converted_partial, number_converted_partial, len(flagged)))
            else:
                L.info('Metadata not upgraded.')
        else:
            L.info('No posts found with special tags or section metadata.  No action is required.')
            L.info('You can safely set the USE_TAG_METADATA and the WARN_ABOUT_TAG_METADATA settings to False.')
