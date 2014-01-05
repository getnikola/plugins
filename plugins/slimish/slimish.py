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

"""
Slimish-Jinja2 template handlers.

pip install slimish_jinja to use
https://github.com/thoughtnirvana/slimish-jinja2 for details

"""

try:
    import jinja2
except ImportError:
    jinja2 = None  # NOQA

try:
    from slimish_jinja.lexer import Lexer
    from slimish_jinja.parse import Parser
except:
    Lexer, Parser = (None, None)  # NOQA

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO  # NOQA

from nikola.plugins.template import jinja as nikojinja
from nikola.plugin_categories import TemplateSystem
from nikola.utils import makedirs, req_missing

import os

class SlimishTemplates(nikojinja.JinjaTemplates, TemplateSystem):

    """Support for slimish_jinja templates in Nikola."""

    name = "slimish"
    lookup = None
    dependency_cache = {}

    def jinjify_slim(self, slimsrc):
        """Jinjify a Slim template, based on slimish_jinja.SlimishExtension."""
        newtemp = StringIO()
        lexer = Lexer(iter(slimsrc.splitlines()))
        Parser(lexer, callback=newtemp.write, debug=True).parse()
        return self.lookup.from_string(newtemp.getvalue())

    def get_template_fn(self, name, parent=None, globals=None):
        if parent is not None:
            name = self.join_path(name, parent)

    def render_template(self, template_name, output_name, context):
        """Render the template into output_name using context."""
        # Dependency check.
        missing = []
        if jinja2 is None:
            missing.append('jinja2')
        if Lexer is None:
            missing.append('slimish_jinja')

        if missing:
            req_missing(missing, 'use this theme')

        src = self.lookup.loader.get_source(self.lookup, template_name)[0]
        template_jinja = self.lookup.get_template(template_name)

        for searchpath in self.lookup.loader.searchpath:
            if os.path.exists(os.path.join(searchpath, template_name)):
                themedir = os.path.split(searchpath)[0]
                break

        try:
            with open(os.path.join(themedir, 'slim')) as fh:
                slim_templates = [l.strip() for l in fh]
        except NotImplementedError:
            slim_templates = []

        if template_name in slim_templates:
            output = self.jinjify_slim(src).render(**context)
        else:
            output = template_jinja.render(**context)

        if output_name is not None:
            makedirs(os.path.dirname(output_name))
            with open(output_name, 'w+') as output:
                output.write(output.encode('utf8'))
        return output
