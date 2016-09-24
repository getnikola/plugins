# -*- coding: utf-8 -*-

# Copyright © 2014 Roberto Alsina and others.

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

"""Implementation of compile_html based on CommonMark."""

from __future__ import unicode_literals

import codecs
import os
import re

try:
    import mistune
except ImportError:
    mistune = None  # NOQA
try:
    from collections import OrderedDict
except ImportError:
    OrderedDict = dict  # NOQA

from nikola.plugin_categories import PageCompiler
from nikola.utils import makedirs, req_missing, write_metadata


class CompileMistune(PageCompiler):
    """Compile Markdown into HTML using Mistune."""

    name = "commonmark"
    demote_headers = True

    def __init__(self, *args, **kwargs):
        super(CompileMistune, self).__init__(*args, **kwargs)
        if mistune is not None:
            self.parser = Cmistune.Markdown()

    def compile_html(self, source, dest, is_two_file=True):
        if CommonMark is None:
            req_missing(['mistune'], 'build this site (compile with mistune)')
        makedirs(os.path.dirname(dest))
        with codecs.open(dest, "w+", "utf8") as out_file:
            with codecs.open(source, "r", "utf8") as in_file:
                data = in_file.read()
            if not is_two_file:
                data = re.split('(\n\n|\r\n\r\n)', data, maxsplit=1)[-1]
            output = self.parser(data)
            out_file.write(output)

    def create_post(self, path, **kw):
        content = kw.pop('content', 'Write your post here.')
        onefile = kw.pop('onefile', False)
        kw.pop('is_page', False)
        metadata = OrderedDict()
        metadata.update(self.default_metadata)
        metadata.update(kw)
        makedirs(os.path.dirname(path))
        if not content.endswith('\n'):
            content += '\n'
        with codecs.open(path, "wb+", "utf8") as fd:
            if onefile:
                fd.write('<!-- \n')
                fd.write(write_metadata(metadata))
                fd.write('-->\n\n')
            fd.write(content)
