# -*- coding: utf-8 -*-

# Copyright © 2019 Roberto Alsina and others.

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

"""
Support for Observable Notebooks (see https://observablehq.com)
"""

import io
import os

from nikola import shortcodes as sc
from nikola.plugin_categories import PageCompiler
from nikola.utils import makedirs, write_metadata

TEMPLATE = """
<!DOCTYPE html>
<body>
<script type="module">

// Load the Observable runtime and inspector.
import {Runtime, Inspector} from "https://cdn.jsdelivr.net/npm/@observablehq/runtime@4/dist/runtime.js";

// Your notebook, compiled as a function.
%s

// Load the notebook, observing its cells with a default Inspector
// that simply renders the value of each cell into the provided DOM node.
new Runtime().module(notebook, Inspector.into(document.querySelector("#notebook_container")));

</script>
<div id="notebook_container"></div>
"""


class CompileObservable(PageCompiler):
    """Compile Observable Notebooks into HTML."""

    name = "observable"
    friendly_name = "Observable Notebooks"
    supports_metadata = False
    supports_onefile = False

    def compile_string(
        self, data, source_path=None, is_two_file=True, post=None, lang=None
    ):
        """Compile notebook into HTML strings, with shortcode support."""
        if not is_two_file:
            _, data = self.split_metadata(data, post, lang)
        new_data, shortcodes = sc.extract_shortcodes(data)
        return self.site.apply_shortcodes_uuid(
            new_data, shortcodes, filename=source_path, extra_context={"post": post}
        )

    def compile(self, source, dest, is_two_file=True, post=None, lang=None):
        """Compile the source file into HTML and save as dest."""
        makedirs(os.path.dirname(dest))
        with io.open(dest, "w+", encoding="utf8") as out_file:
            with io.open(source, "r", encoding="utf8") as in_file:
                data = in_file.read()
                data, shortcode_deps = self.compile_string(
                    data, source, is_two_file, post, lang
                )
            # Make the ES module into a plain function
            data = data.replace(
                "export default function define", "function notebook", 1
            )
            data = TEMPLATE % data
            out_file.write(data)
        if post is None:
            if shortcode_deps:
                self.logger.error(
                    "Cannot save dependencies for post {0} (post unknown)", source
                )
        else:
            post._depfile[dest] += shortcode_deps
        return True

    def create_post(self, path, **kw):
        """Create a new post."""
        content = kw.pop("content", None)
        onefile = kw.pop("onefile", False)
        if onefile:
            self.logger.warning(
                "The observable compiler only supports two-file format."
            )
        # is_page is not used by create_post as of now.
        kw.pop("is_page", False)
        metadata = {}
        metadata.update(self.default_metadata)
        metadata.update(kw)
        makedirs(os.path.dirname(path))
        if not content.endswith("\n"):
            content += "\n"
        with io.open(path, "w+", encoding="utf8") as fd:
            fd.write(content)
