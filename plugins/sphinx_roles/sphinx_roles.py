# -*- coding: utf-8 -*-

# Copyright © 2012-2013 Roberto Alsina and others.

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


class Plugin(RestExtension):

    name = "rest_sphinx_roles"

    def set_site(self, site):
        self.site = site
        roles.register_local_role('pep', pep_role)
        return super(Plugin, self).set_site(site)


def pep_role(name, rawtext, text, lineno, inliner, options={}, content=[]):
    """Enhanced PEP role supporting anchors, for SPhinx compatibility."""
    anchor = ''
    anchorindex = text.find('#')
    if anchorindex > 0:
        text, anchor = text[:anchorindex], text[anchorindex:]
    try:
        pepnum = int(text)
    except ValueError:
        msg = inliner.reporter.error('invalid PEP number %s' % text, line=lineno)
        prb = inliner.problematic(rawtext, rawtext, msg)
        return [prb], [msg]
    ref = inliner.document.settings.pep_base_url + 'pep-%04d' % pepnum
    sn = nodes.strong('PEP ' + text, 'PEP ' + text)
    rn = nodes.reference('', '', internal=False, refuri=ref + anchor,
                         classes=[name])
    rn += sn
    return [rn], []
