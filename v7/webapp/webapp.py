# -*- coding: utf-8 -*-

# Copyright © 2015 The Coil Contributors
# Copyright © 2014 Roberto Alsina

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

from __future__ import print_function, unicode_literals
from nikola.plugin_categories import Command

import webbrowser


class WebAppCoilAdvertisement(Command):

    name = "webapp"
    doc_usage = ""
    doc_purpose = "deprecated, use Coil CMS instead"
    cmd_options = [
        {
            'name': 'browser',
            'short': 'b',
            'type': bool,
            'help': 'Start a web browser.',
            'default': False,
        },
        {
            'name': 'port',
            'short': 'p',
            'long': 'port',
            'default': 8001,
            'type': int,
            'help': 'Port nummber (default: 8001)',
        },
    ]

    def _execute(self, options, args):
        print("Nikola WebApp is not available anymore. It has been replaced by Coil CMS.")
        print("Coil CMS is a full-featured CMS, ready to be used everywhere from small single-user sites environments to big corporate blogs.")
        print("The most basic setup does not require a database and can be done in 2 minutes.")
        print("Coil setup guide: http://coil.readthedocs.org/admin/setup/")
        if options and options.get('browser'):
            webbrowser.open('http://coil.readthedocs.org/admin/setup')
