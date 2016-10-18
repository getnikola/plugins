# -*- coding: utf-8 -*-

# Copyright © 2012-2013 Puneeth Chaganti and others.

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

""" Implementation of compile_html based on Emacs Org-mode.

You will need to install emacs and org-mode (v8.x or greater).

"""

from __future__ import unicode_literals
import codecs
import os
from os.path import abspath, dirname, join
import subprocess

try:
    from collections import OrderedDict
except ImportError:
    OrderedDict = dict  # NOQA

from nikola.plugin_categories import PageCompiler
from nikola.utils import req_missing, makedirs

# v6 compat
try:
    from nikola.utils import write_metadata
except ImportError:
    write_metadata = None  # NOQA


class CompileOrgmode(PageCompiler):
    """ Compile org-mode markup into HTML using emacs. """

    name = "orgmode"

    def compile_html(self, source, dest, is_two_file=True):
        makedirs(os.path.dirname(dest))
        try:
            command = [
                'emacs', '--batch',
                '-l', join(dirname(abspath(__file__)), 'init.el'),
                '--eval', '(nikola-html-export "{0}" "{1}")'.format(
                    abspath(source), abspath(dest))
            ]

            # Dirty walkaround for this plugin to run on Windows platform.
            if os.name == 'nt':
                command[5] = command[5].replace("\\", "\\\\")

            subprocess.check_call(command)
            try:
                post = self.site.post_per_input_file[source]
            except KeyError:
                post = None
            with open(dest, 'r', encoding='utf-8') as inf:
                output, shortcode_deps = self.site.apply_shortcodes(inf.read(), with_dependencies=True)
            with open(dest, 'w', encoding='utf-8') as outf:
                outf.write(output)
            if post is None:
                if shortcode_deps:
                    self.logger.error(
                        "Cannot save dependencies for post {0} due to unregistered source file name",
                        source)
            else:
                post._depfile[dest] += shortcode_deps
        except OSError as e:
            import errno
            if e.errno == errno.ENOENT:
                req_missing(['emacs', 'org-mode'],
                            'use the orgmode compiler', python=False)
        except subprocess.CalledProcessError as e:
                raise Exception('Cannot compile {0} -- bad org-mode '
                                'configuration (return code {1})'.format(
                                    source, e.returncode))

    def create_post(self, path, **kw):
        content = kw.pop('content', None)
        onefile = kw.pop('onefile', False)
        kw.pop('is_page', False)

        metadata = OrderedDict()
        metadata.update(self.default_metadata)
        metadata.update(kw)
        makedirs(os.path.dirname(path))

        with codecs.open(path, "wb+", "utf8") as fd:
            if onefile:
                fd.write("#+BEGIN_COMMENT\n")
                if write_metadata:
                    fd.write(write_metadata(metadata))
                else:
                    for k, v in metadata.items():
                        fd.write('.. {0}: {1}\n'.format(k, v))
                fd.write("#+END_COMMENT\n")
                fd.write("\n\n")

            if content:
                fd.write(content)
            else:
                fd.write('Write your post here.')
