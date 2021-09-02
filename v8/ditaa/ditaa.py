# -*- coding: utf-8 -*-

# Copyright © 2021 Luke Plant

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

"""Custom reST_ directive for ditaa_ integration.
.. _reST: http://docutils.sourceforge.net/rst.html
.. _ditaa: https://github.com/stathissideris/ditaa/
"""

import hashlib
import os
import subprocess
import tempfile

from docutils.nodes import image, literal_block
from docutils.parsers.rst import Directive, directives
from nikola.plugin_categories import RestExtension

OUTPUT_DIR = None  # Set below
OUTPUT_URL_PATH = None  # Set below


class Ditaa(Directive):
    required_arguments = 0
    optional_arguments = 0
    has_content = True

    option_spec = {
        'filename': directives.path,
        'class': directives.class_option,
        'alt': directives.unchanged,
        'cmdline': directives.unchanged,
    }

    def run(self):
        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)

        nodes = []

        body = '\n'.join(self.content)
        tf = tempfile.NamedTemporaryFile(delete=False)
        tf.write(body.encode('utf8'))
        tf.flush()

        # make a filename
        filename_template = self.options.pop('filename', '{checksum}.png')
        filename = filename_template.format({
            'checksum': hashlib.sha256(body.encode('utf-8')).hexdigest()[0:12],
        })

        alt = self.options.get('alt', 'ditaa diagram')
        classes = self.options.pop('class', ['ditaa'])
        cmdline_opts = self.options.pop('cmdline', '').split(' ')

        cmdline = [
            'ditaa',
            tf.name,
            os.path.join(OUTPUT_DIR, filename),
            '--overwrite',
            '--encoding', 'utf8',
        ] + cmdline_opts

        try:
            p = subprocess.run(cmdline, capture_output=True)
        except Exception as exc:
            error = self.state_machine.reporter.error(
                'Failed to run ditaa: %s' % (exc, ),
                literal_block(self.block_text, self.block_text),
                line=self.lineno)
            nodes.append(error)
        else:
            if p.returncode == 0:
                url = OUTPUT_URL_PATH + '/' + filename
                imgnode = image(uri=url, classes=classes, alt=alt)
                nodes.append(imgnode)
            else:
                error = self.state_machine.reporter.error(
                    'Error in "%s" directive: %s' % (self.name, p.stderr),
                    literal_block(self.block_text, self.block_text),
                    line=self.lineno)
                nodes.append(error)
        finally:
            os.unlink(tf.name)

        self.state.document.settings.record_dependencies.add("####MAGIC####CONFIG:DITAA_OUTPUT_URL_PATH")
        return nodes


class Plugin(RestExtension):

    name = "ditaa"

    def set_site(self, site):
        global OUTPUT_DIR, OUTPUT_URL_PATH
        directives.register_directive('ditaa', Ditaa)
        OUTPUT_DIR = site.config['DITAA_OUTPUT_FOLDER']
        OUTPUT_URL_PATH = site.config['DITAA_OUTPUT_URL_PATH']
        return super(Plugin, self).set_site(site)
