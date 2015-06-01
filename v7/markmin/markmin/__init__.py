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

"""Implementation of compile_html based on markmin."""

import codecs
import os
import subprocess

from nikola.plugin_categories import PageCompiler
from nikola.utils import makedirs, req_missing, write_metadata
from . import markmin2html as m2h

try:
    from collections import OrderedDict
except ImportError:
    OrderedDict = dict  # NOQA


class CompileMarkmin(PageCompiler):
    """Compile markmin into HTML."""

    name = "markmin"
    demote_headers = True

    def compile_html(self, source, dest, is_two_file=True):
        makedirs(os.path.dirname(dest))
        binary = self.site.config.get('ASCIIDOC_BINARY', 'markmin')
        try:
            with codecs.open(source, "rb+", "utf8") as in_f:
                with codecs.open(source, "wb+", "utf8") as out_f:
                    body=markmin2html(in_f.read(), pretty_print=True)
                    out_f.write(body)
        except OSError as e:
            if e.strreror == 'No such file or directory':
                req_missing(['markmin'], 'build this site (compile with markmin)', python=False)

    def create_post(self, path, **kw):
        content = kw.pop('content', 'Write your post here.')
        one_file = kw.pop('onefile', False)  # NOQA
        is_page = kw.pop('is_page', False)  # NOQA
        metadata = OrderedDict()
        metadata.update(self.default_metadata)
        metadata.update(kw)
        makedirs(os.path.dirname(path))
        if not content.endswith('\n'):
            content += '\n'
        with codecs.open(path, "wb+", "utf8") as fd:
            if one_file:
                fd.write(write_metadata(metadata))
            fd.write(content)
