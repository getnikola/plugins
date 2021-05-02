# -*- coding: utf-8 -*-

# Copyright © 2016 Manuel Kaufmann

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

from __future__ import unicode_literals

import sys

from docutils import nodes
from docutils.parsers.rst import Directive, directives

from nikola.plugin_categories import RestExtension


class Plugin(RestExtension):

    name = "meta_template"

    def set_site(self, site):
        self.site = site
        MetaTemplate.site = site
        return super(Plugin, self).set_site(site)


class MetaTemplate(Directive):
    """ Restructured text extension for inserting custom templates."""

    option_spec = {
        'title': directives.unchanged,
        'href': directives.unchanged,
        'url': directives.unchanged,
        'target': directives.unchanged,
        'src': directives.unchanged,
        'style': directives.unchanged,
    }

    option_spec.update({f'template_{num:02d}': directives.unchanged for num in range(100)})

    has_content = True
    required_arguments = 1
    optional_arguments = sys.maxsize

    def __init__(self, *args, **kwargs):
        super(MetaTemplate, self).__init__(*args, **kwargs)

    def run(self):
        template_name = self.arguments[0] + '.tmpl'
        self.options.update({
            'content': self.content,
        })
        output = self.site.template_system.render_template(
            template_name,
            None,
            self.options,
        )
        return [nodes.raw('', output, format='html')]


directives.register_directive('template', MetaTemplate)
