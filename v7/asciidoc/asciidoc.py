# -*- coding: utf-8 -*-

# Copyright © 2012-2014 Roberto Alsina and others.

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

"""Implementation of compile_html based on asciidoc.

You will need, of course, to install asciidoc

"""

import codecs
import os
import subprocess

from nikola.plugin_categories import PageCompiler
from nikola.utils import makedirs, req_missing, write_metadata

try:
    from collections import OrderedDict
except ImportError:
    OrderedDict = dict  # NOQA


class CompileAsciiDoc(PageCompiler):
    """Compile asciidoc into HTML."""

    name = "asciidoc"
    demote_headers = True

    def compile(self, source, dest, is_two_file=True, post=None, lang=None):
        """Compile the source file into HTML and save as dest."""
        makedirs(os.path.dirname(dest))
        binary = self.site.config.get('ASCIIDOC_BINARY', 'asciidoc')
        try:
            subprocess.check_call((binary, '-b', 'html5', '-s', '-o', dest, source))
            with open(dest, 'r', encoding='utf-8') as inf:
                output, shortcode_deps = self.site.apply_shortcodes(inf.read(), with_dependencies=True)
            with open(dest, 'w', encoding='utf-8') as outf:
                outf.write(output)
            if post is None:
                if shortcode_deps:
                    self.logger.error(
                        "Cannot save dependencies for post {0} (post unknown)",
                        source)
            else:
                post._depfile[dest] += shortcode_deps
        except OSError as e:
            print(e)
            req_missing(['asciidoc'], 'build this site (compile with asciidoc)', python=False)

    def compile_html(self, source, dest, is_two_file=True):
        """Compile the post into HTML (deprecated API)."""
        try:
            post = self.site.post_per_input_file[source]
        except KeyError:
            post = None

        return compile(source, dest, is_two_file, post, None)

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
                fd.write("////\n")
                fd.write(write_metadata(metadata))
                fd.write("////\n")
            fd.write(content)
