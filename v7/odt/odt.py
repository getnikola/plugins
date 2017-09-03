# -*- coding: utf-8 -*-

# Copyright © 2015 Roberto Alsina and others.

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

"""Implementation of compile_html based on odfpy.

You will need, of course, to install odfpy

"""

import os
import io
import shutil

import lxml.etree as etree

from nikola.plugin_categories import PageCompiler
from nikola.utils import makedirs, req_missing

try:
    from odf.odf2xhtml import ODF2XHTML
except ImportError:
    ODF2XHTML = None

try:
    from collections import OrderedDict
except ImportError:
    OrderedDict = dict  # NOQA


class CompileODT(PageCompiler):
    """Compile ODT into HTML."""

    name = "odt"

    def compile(self, source, dest, is_two_file=True, post=None, lang=None):
        """Compile the source file into HTML and save as dest."""
        makedirs(os.path.dirname(dest))
        if ODF2XHTML is None:
            req_missing(['odfpy'], 'build this site (compile odt)')
        odhandler = ODF2XHTML(True, False)
        data = odhandler.odf2xhtml(source)

        # Take the CSS from the head and put it in body
        doc = etree.fromstring(data)
        body = doc.find('{http://www.w3.org/1999/xhtml}body')

        for style in doc.findall('*//{http://www.w3.org/1999/xhtml}style'):
            style.getparent().remove(style)

            # keep only classes:
            filtered = []
            for line in style.text.splitlines():
                if line and line[0] in '.\t}':
                    filtered.append(line)
            style.text = ''.join(filtered)

            body.insert(0, style)

        with io.open(dest, 'w+', encoding='utf-8') as outf:
            outf.write(etree.tostring(body, encoding='unicode'))

    def compile_html(self, source, dest, is_two_file=True):
        """Compile the post into HTML (deprecated API)."""
        try:
            post = self.site.post_per_input_file[source]
        except KeyError:
            post = None

        return compile(source, dest, is_two_file, post, None)

    def create_post(self, path, **kw):
        onefile = kw.pop('onefile', False)
        # is_page is not used by create_post as of now.
        kw.pop('is_page', False)
        if onefile:
            raise Exception('The one-file format is not supported by this compiler.')
        shutil.copyfile(os.path.join(os.path.dirname(__file__), 'empty.odt'), path)
