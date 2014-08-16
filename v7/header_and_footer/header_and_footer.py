# -*- coding: utf-8 -*-
#
# Copyright © 2014 Reed Wade <reed@typist.geek.nz>
#
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

import codecs
import os
import sys


from nikola.plugin_categories import LateTask
from nikola.utils import get_logger
from nikola.post import Post

defaults = [{
    'source'      : 'header-and-footer/index.html',
    'separator'   : 'piggy',
    'header'      : 'header-and-footer/header',
    'footer'      : 'header-and-footer/footer',
    }]

testing_defaults = [{
    'source'      : 'header-and-footer/index.html',
    'separator'   : 'piggy',
    'header'      : 'header-and-footer/header',
    'footer'      : 'header-and-footer/footer',
    },
    {
    'source'      : 'header-and-footer/index.html',
    'separator'   : 'piggy',
    'header'      : 'test2/$LANG/head',
    'footer'      : 'test2/$LANG/foot',
    }]

# defaults = testing_defaults




class HeaderAndFooter(LateTask):
    """Make header and footer files."""
    name = "header_and_footer"

    doc_usage = ""
    doc_purpose = "make header and footer files containing site nav and markup"

    logger = None

    def gen_tasks(self):
        """Create tasks to generate the header and footer files.
        """

        self.logger = get_logger('header_and_footer', self.site.loghandlers)

        kw = {
            'header_and_footer': self.site.config.get('HEADER_AND_FOOTER', defaults),
            'output_folder': self.site.config['OUTPUT_FOLDER'],
            'translations': self.site.config['TRANSLATIONS'],
        }

        def make_header_and_footer():
            verbose = self.site.config.get('HEADER_AND_FOOTER_VERBOSE', False)

            for entry in kw['header_and_footer']:
                if not entry.get('source'):
                    self.logger.error("missing source setting")
                    continue

                for lang in kw['translations']:

                    file_name = os.path.join(kw['output_folder'], entry['source'].replace('$LANG',lang))
                    if verbose:
                        self.logger.info("reading {file_name}".format(file_name=file_name))
                    if not os.path.exists(file_name):
                        self.logger.error('missing {file_name}'.format(file_name=file_name))
                        continue

                    with codecs.open(file_name, encoding='utf-8') as f:
                        contents = f.read()

                    if entry['separator'] not in contents:
                        self.logger.error('missing marker in {file_name}'.format(file_name=file_name))
                        continue

                    #
                    # rewrite url references for images, css, js to point to root level
                    #
                    # TODO: does this cover all the cases we care about?
                    #
                    contents = contents.replace('="../', '="/')

                    header_content, footer_content = contents.split(entry['separator'], 1)


                    header_path = os.path.join(
                        kw['output_folder'], entry['header'].replace('$LANG',lang))
                    footer_path = os.path.join(
                        kw['output_folder'], entry['footer'].replace('$LANG',lang))

                    if not os.path.exists(os.path.dirname(header_path)):
                        os.makedirs(os.path.dirname(header_path))
                    if not os.path.exists(os.path.dirname(footer_path)):
                        os.makedirs(os.path.dirname(footer_path))

                    with codecs.open(header_path, encoding='utf-8', mode='w') as f:
                        f.write(header_content)

                    if verbose:
                        self.logger.info('wrote {header_path}'.format(header_path=header_path))

                    with codecs.open(footer_path, encoding='utf-8', mode='w') as f:
                        f.write(footer_content)

                    if verbose:
                        self.logger.info('wrote {footer_path}'.format(footer_path=footer_path))


        yield {
            'actions' : [make_header_and_footer],
            'basename': self.name,
        }




