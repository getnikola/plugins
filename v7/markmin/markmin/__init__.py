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
import re

from nikola.plugin_categories import PageCompiler
from nikola.utils import makedirs, write_metadata
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
        with codecs.open(source, "rb+", "utf8") as in_f:
            with codecs.open(dest, "wb+", "utf8") as out_f:
                data = in_f.read()
                if not is_two_file:
                    spl = re.split('(\n\n|\r\n\r\n)', data, maxsplit=1)
                    data = spl[-1]
                output = m2h.markmin2html(data, pretty_print=True)
                output, shortcode_deps = self.site.apply_shortcodes(output, filename=source, with_dependencies=True, extra_context=dict(post=post))
                out_f.write(output)
        if post is None:
            if shortcode_deps:
                self.logger.error(
                    "Cannot save dependencies for post {0} due to unregistered source file name",
                    source)
        else:
            post._depfile[dest] += shortcode_deps

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
                fd.write('\n')
            fd.write(content)
