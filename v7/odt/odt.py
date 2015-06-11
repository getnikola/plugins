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
import subprocess
import shutil

import lxml.etree as etree

from nikola.plugin_categories import PageCompiler
from nikola.utils import makedirs, req_missing

try:
    from collections import OrderedDict
except ImportError:
    OrderedDict = dict  # NOQA


class CompileODT(PageCompiler):
    """Compile ODT into HTML."""

    name = "odt"

    def compile_html(self, source, dest, is_two_file=True):
        makedirs(os.path.dirname(dest))
        binary = 'odf2xhtml'
        try:
            data = subprocess.check_output((binary, source))

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

            with open(dest, 'wb+') as outf:
                outf.write(etree.tostring(body, encoding='unicode'))
        except OSError as e:
            if e.strreror == 'No such file or directory':
                req_missing(['odfpy'], 'build this site (compile with odt)', python=False)

    def create_post(self, path, **kw):
        onefile = kw.pop('onefile', False)
        # is_page is not used by create_post as of now.
        kw.pop('is_page', False)
        if onefile:
            raise Exception('The one-file format is not supported by this compiler.')
        shutil.copyfile(os.path.join(os.path.dirname(__file__), 'empty.odt'), path)
