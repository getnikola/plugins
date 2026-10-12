# -*- coding: utf-8 -*-

# Copyright © 2018 Santos Gallegos.

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
Add the ``config`` role, it reads a value from the `conf.py` file.

Usage:

   Send us an email to :config:`BLOG_EMAIL`

Here `BLOG_EMAIL` is the variable name from the conf.py file.
Note that the text is rendered as an email link, not just as plain text.
This is because the value is interpreted as reStructuredText.
"""

from docutils.frontend import OptionParser
from docutils.parsers.rst import Parser, roles
from docutils.utils import new_document
from nikola.plugin_categories import RestExtension


class Plugin(RestExtension):

    name = 'config_role'

    def set_site(self, site):
        roles.register_canonical_role('config', config_role(site))
        return super().set_site(site)


def config_role(site):
    """
    Inject a value from the ``conf.py`` file.

    Before injecting the value, it is parsed by the rst parser,
    that way we can have a link when reading an email from the config
    for example.

    This role needs access to the `site` object.
    As we can't pass extra args to a role function we are using a closure.
    """
    def role(name, rawtext, text, lineno, inliner, options=None, content=None):
        parser = Parser()
        settings = OptionParser(components=(Parser,)).get_default_values()
        document = new_document('Raw rst from config value', settings)

        config_value = site.config.get(text, '')
        parser.parse(config_value, document)

        # The whole text is interpreted as a big paragraph
        # causing a new line to be inserted at the end,
        # so we only take the elements inside that paragraph.
        paragraph, *_ = document.children
        return paragraph.children, []
    return role
