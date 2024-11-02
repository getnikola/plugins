# -*- coding: utf-8 -*-

# A WordPress compiler plugin for Nikola
#
# Copyright (C) 2014-2015 by Felix Fontein
# Copyright (C) by the WordPress contributors
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import nikola.plugin_categories

import re
import regex

import pygments
import pygments.lexers
import pygments.lexers.special
import pygments.formatters


class Code(nikola.plugin_categories.CompilerExtension):
    name = 'wordpress_shortcode_code'
    compiler_name = 'wordpress'

    def __init__(self):
        super(Code, self).__init__()

    def _filter_code_tags(self, text, context):
        result = ''
        for piece in regex.split(r'(\[code(?:|\s+language="[^"]*?")\].*?\[/code\])', text, flags=regex.DOTALL | regex.IGNORECASE):
            match = regex.match(r'\[code(?:|\s+language="([^"]*?)")\](.*?)\[/code\]', piece, flags=regex.DOTALL | regex.IGNORECASE)
            if match is not None:
                the_id = str(context.inc_plugin_counter('wordpress_shortcode_code', 'counter'))
                context.store_plugin_data('wordpress_shortcode_code', the_id, (match.group(2), match.group(1)))
                result += '[code id="{0}"]'.format(the_id)
            else:
                result += piece
        return result

    def _replace_code_tags(self, args, content, tag, context):
        the_id = args['id']
        codeContent, codeType = context.get_plugin_data('wordpress_shortcode_code', the_id)
        if codeType is None:
            lexer = pygments.lexers.special.TextLexer()
            codeType = 'unformatted'
        else:
            lexer = pygments.lexers.get_lexer_by_name(codeType)
        # The following regular expression and its applications are taken from Nikola's plugins/task/listings.py; Copyright © 2012-2015 Roberto Alsina and others
        CODERE = re.compile('<div class="code"><pre>(.*?)</pre></div>', flags=re.MULTILINE | re.DOTALL)
        if codeContent.find('\n') >= 0 or codeContent.find('\r') >= 0:
            content = pygments.highlight(codeContent, lexer, pygments.formatters.HtmlFormatter(cssclass='code', linenos='inline', nowrap=False, anchorlinenos=False))
            content = CODERE.sub('<pre class="code literal-block">\\1</pre>', content.strip('\n'))
            return "<div class='code-" + codeType + "'>" + content + "</div>"
        else:
            content = pygments.highlight(codeContent, lexer, pygments.formatters.HtmlFormatter(cssclass='code', linenos=False, nowrap=False, anchorlinenos=False))
            content = CODERE.sub('<code class="code literal-block">\\1</code>', content).replace("\n", "")
            return "<span class='code-" + codeType + " inline-code'>" + content + "</span>"

    def register(self, compile_wordpress, wordpress_modules):
        self._user_logged_in = False
        self._compile_wordpress = compile_wordpress
        compile_wordpress.register_shortcode('code', self._replace_code_tags)
        compile_wordpress.add_filter('the_content', self._filter_code_tags, 1)
