# -*- coding: utf-8 -*-

# Copyright © 2012-2018 Roberto Alsina and others.

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

"""Page compiler plugin for Python Modules using PDoc."""


import io
import os
import shlex
import subprocess
import tempfile


from nikola import shortcodes as sc
from nikola.plugin_categories import PageCompiler
from nikola.utils import makedirs, write_metadata


class CompilePdoc(PageCompiler):
    """Compile docstrings into HTML."""

    name = "pdoc"
    friendly_name = "PDoc"
    supports_metadata = True

    def compile_string(self, data, source_path=None, is_two_file=True, post=None, lang=None):
        """Compile docstrings into HTML strings, with shortcode support."""
        if not is_two_file:
            _, data = self.split_metadata(data, post, lang)
        new_data, shortcodes = sc.extract_shortcodes(data)
        # The way pdoc generates output is a bit inflexible
        with tempfile.TemporaryDirectory() as tmpdir:
            subprocess.check_call(['pdoc', '--html', '--html-dir', tmpdir] + shlex.split(data.strip()))
            fname = os.listdir(tmpdir)[0]
            with open(fname, 'r', encoding='utf8') as inf:
                output = inf.read()
        return self.site.apply_shortcodes_uuid(output, shortcodes, filename=source_path, extra_context={'post': post})

    def compile(self, source, dest, is_two_file=True, post=None, lang=None):
        """Compile the docstring into HTML and save as dest."""
        makedirs(os.path.dirname(dest))
        with io.open(dest, "w+", encoding="utf8") as out_file:
            with io.open(source, "r", encoding="utf8") as in_file:
                data = in_file.read()
            data, shortcode_deps = self.compile_string(data, source, is_two_file, post, lang)
            out_file.write(data)
        if post is None:
            if shortcode_deps:
                self.logger.error(
                    "Cannot save dependencies for post {0} (post unknown)",
                    source)
        else:
            post._depfile[dest] += shortcode_deps
        return True

    def create_post(self, path, **kw):
        """Create a new post."""
        content = kw.pop('content', None)
        onefile = kw.pop('onefile', False)
        # is_page is not used by create_post as of now.
        kw.pop('is_page', False)
        metadata = {}
        metadata.update(self.default_metadata)
        metadata.update(kw)
        makedirs(os.path.dirname(path))
        if not content.endswith('\n'):
            content += '\n'
        with io.open(path, "w+", encoding="utf8") as fd:
            if onefile:
                fd.write(write_metadata(metadata, comment_wrap=True, site=self.site, compiler=self))
            fd.write(content)
