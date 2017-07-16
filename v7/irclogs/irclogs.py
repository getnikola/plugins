# -*- coding: utf-8 -*-

# Copyright © 2014–2015, Chris Warrick.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions, and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions, and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# 3. Neither the name of the author of this software nor the names of
#    contributors to this software may be used to endorse or promote
#    products derived from this software without specific prior written
#    consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""Implementation of compile_html for IRC logs."""

from __future__ import unicode_literals

import os
import io
import re
import pygments
import pygments.lexers

from nikola.plugin_categories import PageCompiler
from nikola.utils import makedirs, NikolaPygmentsHTML

lexer = pygments.lexers.get_lexer_by_name('irc')


class CompileIRCLogs(PageCompiler):
    """Compile IRC logs into HTML."""
    name = "irclogs"

    def compile(self, source, dest, is_two_file=True, post=None, lang=None):
        """Compile the source file into HTML and save as dest."""
        """Compile into HTML, using NikolaPygmentsHTML."""
        makedirs(os.path.dirname(dest))
        with io.open(dest, "w+", encoding="utf8") as out_file:
            with io.open(source, "r", encoding="utf8") as in_file:
                data = in_file.read()

            formatter = NikolaPygmentsHTML('irclog', linenos=False)
            data = pygments.highlight(data, lexer, formatter)
            link_matcher = re.compile(r"(http[s]?://[^\s]+)")
            data = link_matcher.sub(r'<a href="\1" rel="nofollow">\1</a>', data)
            out_file.write(data)
