# -*- coding: utf-8 -*-

# Copyright © 2016 Mike Ray and others.

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

"""Implementation of compile_html based on kramdown.

kramdown is available in the repos of several distributions.

For Debian:

sudo apt-get install ruby-kramdown

"""

import io
import os
import subprocess
import tempfile

from nikola.plugin_categories import PageCompiler
from nikola.utils import makedirs, write_metadata


class CompileKramdown(PageCompiler):
    """Compile kramdown into HTML."""

    name = "kramdown"
    demote_headers = True

    def compile_string(self, data, source_path=None, is_two_file=True, post=None, lang=None):
        """Compile markdown into HTML strings."""
        if not is_two_file:
            _, data = self.split_metadata(data, post, lang)

        from nikola import shortcodes as sc
        new_data, shortcodes = sc.extract_shortcodes(data)

        # Kramdown takes a file as argument and prints to stdout
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as source:
            source.write(new_data)
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as dest:
            command = ['kramdown', '-o', 'html', '--no-auto-ids', source.name]
            subprocess.check_call(command, stdout=dest)
        with open(dest.name, 'r') as inf:
            output = inf.read()

        os.unlink(source.name)
        os.unlink(dest.name)
        output, shortcode_deps = self.site.apply_shortcodes_uuid(output, shortcodes, filename=source_path, extra_context={'post': post})

        return output, shortcode_deps

    def compile(self, source, dest, is_two_file=True, post=None, lang=None):
        """Compile the source file into HTML and save as dest."""
        makedirs(os.path.dirname(dest))
        with io.open(dest, "w+", encoding="utf8") as out_file:
            with io.open(source, "r", encoding="utf8") as in_file:
                data = in_file.read()
                output, shortcode_deps = self.compile_string(data, source, is_two_file, post, lang)
                out_file.write(output)
                post._depfile[dest] += shortcode_deps
        return True

    def create_post(self, path, content=None, onefile=False, is_page=False, **kw):
        """Create post file with optional metadata."""
        metadata = {}
        metadata.update(self.default_metadata)
        metadata.update(kw)
        makedirs(os.path.dirname(path))
        if not content.endswith('\n'):
            content += '\n'
        with io.open(path, "w+", encoding="utf8") as fd:
            if onefile:
                fd.write("<!--\n")
                fd.write(write_metadata(metadata).strip())
                fd.write("\n-->\n\n")
            fd.write(content)
