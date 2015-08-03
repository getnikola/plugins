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

# This file is based on WordPress' wp-include/shortcodes.php

from . import php

import regex


def shortcode_atts(pairs, atts):
    # * @param array $pairs Entire list of supported attributes and their defaults.
    # * @param array $atts User defined attributes in shortcode tag.
    # * @return array Combined attribute list.
    if type(atts) == str:
        atts = {None: atts}
    out = dict()
    if type(pairs) == dict:
        pairs = pairs.items()
    for key, value in pairs:
        if key in atts:
            out[key] = atts[key]
        else:
            out[key] = value
    return out


class ShortCodes(object):
    def __init__(self):
        self._shortcode_tags = {}
        self._create_shortcode_regex()
        self._detect_any_shortcode_regex = '\\[(\\[?)([\\w-_]+)([^\\]/]*(?:/(?!\\])[^\\]/]*)*?)(?:(/)\\]|\\](?:([^\\[]*+(?:\\[(?!/\\2\\])[^\\[]*+)*+)\\[/\\2\\])?)(\\]?)'
#              '\\['                              # Opening bracket
#            + '(\\[?)'                           # 1: Optional second opening bracket for escaping shortcodes: [[tag]]
#            + "([\\w-_]+)"                       # 2: Shortcode name
#            + '('                                # 3: Unroll the loop: Inside the opening shortcode tag
#            +     '[^\\]/]*'                     # Not a closing bracket or forward slash
#            +     '(?:'
#            +         '/(?!\\])'                 # A forward slash not followed by a closing bracket
#            +         '[^\\]/]*'                 # Not a closing bracket or forward slash
#            +     ')*?'
#            + ')'
#            + '(?:'
#            +     '(/)'                          # 4: Self closing tag ...
#            +     '\\]'                          # ... and closing bracket
#            + '|'
#            +     '\\]'                          # Closing bracket
#            +     '(?:'
#            +         '('                        # 5: Unroll the loop: Optionally, anything between the opening and closing shortcode tags
#            +             '[^\\[]*+'             # Not an opening bracket
#            +             '(?:'
#            +                 '\\[(?!/\\2\\])'   # An opening bracket not followed by the closing shortcode tag
#            +                 '[^\\[]*+'         # Not an opening bracket
#            +             ')*+'
#            +         ')'
#            +         '\\[/\\2\\]'               # Closing shortcode tag
#            +     ')?'
#            + ')'
#            + '(\\]?)'                           # 6: Optional second closing brocket for escaping shortcodes: [[tag]]

    def _create_shortcode_regex(self):
        tagregexp = '|'.join([regex.escape(x) for x in self._shortcode_tags.keys()])

        self._shortcode_regex = '\\[(\\[?)(' + tagregexp + ')(?![\\w-])([^\\]/]*(?:/(?!\\])[^\\]/]*)*?)(?:(/)\\]|\\](?:([^\\[]*+(?:\\[(?!/\\2\\])[^\\[]*+)*+)\\[/\\2\\])?)(\\]?)'
#              '\\['                              # Opening bracket
#            + '(\\[?)'                           # 1: Optional second opening bracket for escaping shortcodes: [[tag]]
#            + "(" + tagregexp + ")"              # 2: Shortcode name
#            + '(?![\\w-])'                       # Not followed by word character or hyphen
#            + '('                                # 3: Unroll the loop: Inside the opening shortcode tag
#            +     '[^\\]/]*'                     # Not a closing bracket or forward slash
#            +     '(?:'
#            +         '/(?!\\])'                 # A forward slash not followed by a closing bracket
#            +         '[^\\]/]*'                 # Not a closing bracket or forward slash
#            +     ')*?'
#            + ')'
#            + '(?:'
#            +     '(/)'                          # 4: Self closing tag ...
#            +     '\\]'                          # ... and closing bracket
#            + '|'
#            +     '\\]'                          # Closing bracket
#            +     '(?:'
#            +         '('                        # 5: Unroll the loop: Optionally, anything between the opening and closing shortcode tags
#            +             '[^\\[]*+'             # Not an opening bracket
#            +             '(?:'
#            +                 '\\[(?!/\\2\\])'   # An opening bracket not followed by the closing shortcode tag
#            +                 '[^\\[]*+'         # Not an opening bracket
#            +             ')*+'
#            +         ')'
#            +         '\\[/\\2\\]'               # Closing shortcode tag
#            +     ')?'
#            + ')'
#            + '(\\]?)'                           # 6: Optional second closing brocket for escaping shortcodes: [[tag]]

    def get_shortcode_tags(self):
        return self._shortcode_tags

    def register_shortcode(self, tag, function):
        self._shortcode_tags[tag] = function
        self._create_shortcode_regex()

    def unregister_shortcode(self, tag):
        del self._shorcode_tags[tag]

    def _extract_arguments(self, argsString):
        pattern = '(\w+)\s*=\s*"([^"]*)"(?:\s|$)|(\w+)\s*=\s*\'([^\']*)\'(?:\s|$)|(\w+)\s*=\s*([^\s\'"]+)(?:\s|$)|"([^"]*)"(?:\s|$)|(\S+)(?:\s|$)'
        argsString = regex.sub("[\u00A0\u200B]+", " ", argsString)
        matches = regex.findall(pattern, argsString)
        if len(matches) > 0:
            result = dict()
            for match in matches:
                if match[0] is not None:
                    result[match[0].lower()] = php.stripcslashes(match[1])
                elif match[2] is not None:
                    result[match[2].lower()] = php.stripcslashes(match[3])
                elif match[4] is not None:
                    result[match[4].lower()] = php.stripcslashes(match[5])
                elif match[6] is not None and len(match[6]) > 0:
                    result[None] = php.stripcslashes(match[6])
                elif match[7] is not None:
                    result[None] = php.stripcslashes(match[7])
            return result
        else:
            return argsString.lstrip()

    def _do_shortcode_tag(self, match, context):
        # In case it is a 'fake' (escaped) shortcode, just plug the text back in
        if match.group(1) == '[' and match.group(6) == ']':
            return match.group(0)

        # Determine shortcode processing function
        tag = match.group(2)
        if tag not in self._shortcode_tags:
            raise Exception("Found unknown shortcode '" + tag + "' (with matcher " + str(match) + ")!")
        func = self._shortcode_tags[tag]

        # Process arguments
        args = self._extract_arguments(match.group(3))

        # Process
        if match.group(5) is not None:
            # Enclosing tag - extra parameter
            return func(args, match.group(5), tag, context)
        else:
            # Self-closing tag
            return func(args, None, tag, context)

    def do_shortcode(self, data, context):
        if len(self._shortcode_tags) == 0:
            return data
        return php.preg_replace_callback(self._shortcode_regex, lambda x: self._do_shortcode_tag(x, context), data, regex.DOTALL | regex.VERSION1)

    def get_containing_shortcodes_set(self, data):
        result = set()
        matches = regex.findall(self._detect_any_shortcode_regex, data)
        for match in matches:
            if match[0] == '[' and match[5] == ']':
                continue
            result.add(match[1])
        return result
