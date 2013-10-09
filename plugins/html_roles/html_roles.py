# -*- coding: utf-8 -*-

# Copyright © 2013 Aru Sahni

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

from docutils import nodes
from docutils.parsers.rst import roles

from nikola.plugin_categories import RestExtension

TAGS = {
    'strike': 'strike',
    'del': 'del',
    'ins': 'ins',
}


class Plugin(RestExtension):

    name = "html_roles"

    def set_site(self, site):
        self.site = site
        for role, tag in TAGS.items():
            roles.register_canonical_role(role, tag_role(tag))
        return super(Plugin, self).set_site(site)


def tag_role(tag):
    """ Generates a role for the specified tag """
    def _spanning_role(role, rawtext, text, lineno, inliner,
                       options={}, content=[]):
        """ reStructuredText role for generating the a tag element """
        return [nodes.raw('', '<{tag}>{text}</{tag}>'.format(
            tag=tag, text=text), format='html')], []
    return _spanning_role
