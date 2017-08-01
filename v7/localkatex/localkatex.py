# -*- coding: utf-8 -*-

# Copyright © 2017, Chris Warrick.

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
import subprocess
import json
import os.path

from nikola.plugin_categories import ShortcodePlugin
from nikola import utils

jspath = os.path.join(os.path.split(__file__)[0], 'localkatex.js')


class LocalKatex(ShortcodePlugin):
    """Render math using KaTeX while building the site."""

    name = 'localkatex'
    _options_available = {'displayMode': bool, 'throwOnError': bool, 'errorColor': str, 'colorIsTextColor': bool}
    logger = None

    def set_site(self, site):
        """Set Nikola site."""
        site.register_shortcode('lmath', self.handler)
        site.register_shortcode('lmathd', self.handler_display)
        self.logger = utils.get_logger('localkatex')
        return super(LocalKatex, self).set_site(site)

    @staticmethod
    def _str_to_bool(v):
        return v.lower() not in ('false', 'no', 'f', 'n')

    def handler(self, site, lang, post, data, **options):
        """Render math."""
        p = subprocess.Popen(['node', jspath], stdin=subprocess.PIPE, stdout=subprocess.PIPE)

        if 'display' in options:
            options['displayMode'] = options['display']
            del options['display']

        for k, v in options.items():
            if k in self._options_available and self._options_available[k] == bool:
                options[k] = self._str_to_bool(v)
            elif k not in self._options_available:
                raise ValueError("Unknown KaTeX option {0}={1}".format(k, v))

        json_input = json.dumps({'math': data, 'options': options}).encode('utf-8')
        stdout, stderr = p.communicate(json_input)
        output = json.loads(stdout.decode('utf-8').strip())
        if output['success']:
            return output['output']
        else:
            if output['input'] is None and output['output'] is None:
                raise Exception("Cannot import KaTeX. Did you run npm install?")
            else:
                self.logger.error("In expression {0}: {1}".format(data, output['output']))
                return '<span class="problematic"><strong>In expression <code>{0}</code>:</strong> {1}</span>'.format(data, output['output'])

    def handler_display(self, site, lang, post, data, **options):
        """Render math in display mode."""
        return self.handler(site, lang, post, data, displayMode='true', **options)
