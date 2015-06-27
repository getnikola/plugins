# A WordPress compiler plugin for Nikola
#
# Copyright (C) 2014-2015 by the contributors
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

import regex


def preg_replace_callback(pattern, callback, text, flags=0):
    pos = 0
    result = ''
    while pos < len(text):
        matcher = regex.search(pattern, text[pos:], flags)
        if matcher is None:
            result += text[pos:]
            break
        result += text[pos:pos + matcher.start()]
        result += callback(matcher)
        pos += matcher.end()
    return result


def stripcslashes(text):
    result = ''
    index = 0
    while index < len(text):
        c = text[index]
        index += 1
        if c == '\\':
            c = text[index]
            index += 1
            if c == '\\':
                result += c
            elif c == 'a':
                result += '\a'
            elif c == 'b':
                result += '\b'
            elif c == 'f':
                result += '\f'
            elif c == 'n':
                result += '\n'
            elif c == 'r':
                result += '\r'
            elif c == 't':
                result += '\t'
            elif c == 'v':
                result += '\v'
            else:
                raise Exception("Unknown escape sequence '\\" + c + "'")
        else:
            result += c
    return result
