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

import codecs
import os
from os.path import abspath, dirname, join
import subprocess
import shutil

from nikola.plugin_categories import PageCompiler
from nikola.utils import LOGGER, makedirs


class CompileOrgmode(PageCompiler):
    """ Compile org-mode markup into HTML using emacs. """

    name = "orgmode"

    def compile_html(self, source, dest, is_two_file=True):
        makedirs(os.path.dirname(dest))
        try:
            command = [
                'emacs', '--batch',
                '-l', '%s' % join(dirname(abspath(__file__)), 'init.el'),
                '--eval', '(nikola-html-export "%s" "%s")' % (abspath(source), abspath(dest))
            ]
            subprocess.check_call(command)
        except OSError as e:
            import errno
            if e.errno == errno.ENOENT:
                LOGGER.error('To use the orgmode compiler,'
                             ' you have to install emacs and org-mode.')
                raise Exception('Cannot compile {0} -- emacs '
                                'missing'.format(source))
        except subprocess.CalledProcessError:
                raise Exception('Cannot compile {0} -- bad org-mode '
                                'configuration'.format(source))


    def create_post(self, path, onefile=False, **kw):
        metadata = {}
        metadata.update(self.default_metadata)
        metadata.update(kw)
        makedirs(os.path.dirname(path))

        with codecs.open(path, "wb+", "utf8") as fd:
            if onefile:
                fd.write("#+BEGIN_COMMENT\n")
                for k, v in metadata.items():
                    fd.write('.. {0}: {1}\n'.format(k, v))
                fd.write("#+END_COMMENT\n")
                fd.write("\n\n")
            fd.write('Write your post here.')
