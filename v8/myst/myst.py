# -*- coding: utf-8 -*-

# Copyright © 2013-2020 Roberto Alsina and others.

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

"""Implementation of compile_html based on Myst."""

import codecs
import os

try:
    import myst_parser

    # this works for myst-parser versions <= 0.17.2
    try:
        from myst_parser.main import to_html
        old_myst = True
    except ImportError:
        from docutils.core import publish_string
        from myst_parser.docutils_ import Parser
        old_myst = False
except ImportError:
    myst_parser = None
    nikola_extension = None
from collections import OrderedDict

from nikola import shortcodes as sc
from nikola.plugin_categories import PageCompiler
from nikola.utils import makedirs, req_missing, write_metadata


class CompileMyst(PageCompiler):
    """Compile Myst into HTML."""

    name = "myst"
    demote_headers = True

    def __init__(self, *args, **kwargs):
        super(CompileMyst, self).__init__(*args, **kwargs)

    def compile_string(
        self, data, source_path=None, is_two_file=True, post=None, lang=None
    ):
        """Compile the source file into HTML strings (with shortcode support).

        Returns a tuple of at least two elements: HTML string [0] and shortcode dependencies [last].
        """
        if myst_parser is None:
            req_missing(["myst-parser"], "build this site (compile with myst)")
        if not is_two_file:
            _, data = self.split_metadata(data, post, lang)
        new_data, shortcodes = sc.extract_shortcodes(data)

        if old_myst:
            output = to_html(new_data)
        else:
            output = publish_string(
                source=new_data,
                writer_name="html5",
                settings_overrides={
                    "myst_enable_extensions":
                        [
                            "attrs_inline",
                            "colon_fence",
                            "deflist",
                            "fieldlist",
                            "html_admonition",
                            "html_image",
                            "linkify",
                            "smartquotes",
                            "strikethrough",
                            "substitution",
                            "tasklist",
                        ],
                    "embed_stylesheet": True,
                    'output_encoding': 'unicode',
                    'myst_suppress_warnings': ["myst.header"],
                    'myst_heading_anchors': 4
                },
                parser=Parser(),
            )
        output, shortcode_deps = self.site.apply_shortcodes_uuid(
            output, shortcodes, filename=source_path, extra_context={"post": post}
        )
        return output, shortcode_deps

    def compile(self, source, dest, is_two_file=True, post=None, lang=None):
        """Compile the source file into HTML and save as dest."""
        if myst_parser is None:
            req_missing(["myst-parser"], "build this site (compile with myst)")
        makedirs(os.path.dirname(dest))
        with codecs.open(dest, "w+", "utf8") as out_file:
            with codecs.open(source, "r", "utf8") as in_file:
                data = in_file.read()
            output, shortcode_deps = self.compile_string(
                data, source, is_two_file, post, lang
            )
            out_file.write(output)
        if post is None:
            if shortcode_deps:
                self.logger.error(
                    "Cannot save dependencies for post {0} (post unknown)", source
                )
        else:
            post._depfile[dest] += shortcode_deps

    def create_post(self, path, content=None, onefile=False, is_page=False, **kw):
        """Create post file with optional metadata."""
        metadata = OrderedDict()
        metadata.update(self.default_metadata)
        metadata.update(kw)
        makedirs(os.path.dirname(path))
        if not content.endswith("\n"):
            content += "\n"
        with codecs.open(path, "wb+", "utf8") as fd:
            if onefile:
                fd.write("<!--\n")
                fd.write(write_metadata(metadata).rstrip())
                fd.write("\n-->\n\n")
            fd.write(content)
