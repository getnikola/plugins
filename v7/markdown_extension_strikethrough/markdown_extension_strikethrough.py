# -*- coding: utf-8 -*-

# This is free and unencumbered software released into the public domain.
#
# Anyone is free to copy, modify, publish, use, compile, sell, or
# distribute this software, either in source code form or as a compiled
# binary, for any purpose, commercial or non-commercial, and by any
# means.
#
# In jurisdictions that recognize copyright laws, the author or authors
# of this software dedicate any and all copyright interest in the
# software to the public domain. We make this dedication for the benefit
# of the public at large and to the detriment of our heirs and
# successors. We intend this dedication to be an overt act of
# relinquishment in perpetuity of all present and future rights to this
# software under copyright law.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
# For more information, please refer to <http://unlicense.org/>


from __future__ import print_function, unicode_literals

from nikola.plugin_categories import MarkdownExtension

try:
    from markdown.extensions import Extension
    from markdown.inlinepatterns import SimpleTagPattern
except ImportError:
    # No need to catch this, if you try to use this without Markdown,
    # the markdown compiler will fail first
    Extension = SimpleTagPattern = object


STRIKE_RE = r"(~{2})(.+?)(~{2})"  # ~~strike~~


class StrikethroughMarkdownExtension(MarkdownExtension, Extension):
    """An extension that supports PHP-Markdown style strikethrough.

    For example: ``~~strike~~``.
    """
    name = 'markdown_extension_strikethrough'

    def extendMarkdown(self, md, md_globals):
        pattern = SimpleTagPattern(STRIKE_RE, 'del')
        md.inlinePatterns.add('strikethrough', pattern, '_end')
