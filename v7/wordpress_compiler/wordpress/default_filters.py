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

# This file is based on WordPress' wp-include/formatting.php

from . import php

import regex


def _x(default, lookup):
    return default


class DefaultWordpressFilters:
    def __init__(self, shortcodes):
        super().__init__()
        self.wp_cockneyreplace = None
        self.__wptexturize_setup()
        self.__convert_chars_setup()
        self.option_use_smilies = False  # option!
        self.wp_smiliessearch = []
        self.wpsmiliestrans = {}
        self.shortcode_tags = shortcodes.get_shortcode_tags()

    def __wptexturize_setup(self):
        # translators: opening curly double quote */
        opening_quote = _x('&#8220;', 'opening curly double quote')
        # translators: closing curly double quote */
        closing_quote = _x('&#8221;', 'closing curly double quote')

        # translators: apostrophe, for example in 'cause or can't */
        apos = _x('&#8217;', 'apostrophe')

        # translators: prime, for example in 9' (nine feet) */
        prime = _x('&#8242;', 'prime')
        # translators: double prime, for example in 9" (nine inches) */
        double_prime = _x('&#8243;', 'double prime')

        # translators: opening curly single quote */
        opening_single_quote = _x('&#8216;', 'opening curly single quote')
        # translators: closing curly single quote */
        closing_single_quote = _x('&#8217;', 'closing curly single quote')

        # translators: en dash */
        en_dash = _x('&#8211;', 'en dash')
        # translators: em dash */
        em_dash = _x('&#8212;', 'em dash')

        self.default_no_texturize_tags = ['pre', 'code', 'kbd', 'style', 'script', 'tt']
        self.default_no_texturize_shortcodes = ['code']

        # if a plugin has provided an autocorrect array, use it
        if self.wp_cockneyreplace is not None:
            cockney = list(self.wp_cockneyreplace.keys())
            cockneyreplace = [self.wp_cockneyreplace[key] for key in cockney]
        elif "'" != apos:  # Only bother if we're doing a replacement.
            cockney = ["'tain't", "'twere", "'twas", "'tis", "'twill", "'til", "'bout", "'nuff", "'round", "'cause"]
            cockneyreplace = [apos + "tain" + apos + "t", apos + "twere", apos + "twas", apos + "tis", apos + "twill",
                              apos + "til", apos + "bout", apos + "nuff", apos + "round", apos + "cause"]
        else:
            cockney = []
            cockneyreplace = []

        static_characters = ['---', ' -- ', '--', ' - ', 'xn&#8211;', '...', '``', '\'\'', ' (tm)'] + cockney
        static_replacements = [em_dash, ' ' + em_dash + ' ', en_dash, ' ' + en_dash + ' ', 'xn--', '&#8230;',
                               opening_quote, closing_quote, ' &#8482;'] + cockneyreplace
        self.static = list(zip(static_characters, static_replacements))

        dynamic = []
        if "'" != apos:
            dynamic.append(('\'(\d\d(?:&#8217;|\')?s)', apos + '\\1'))  # '99's
            dynamic.append(('\'(\d)', apos + '\\1'))  # '99
        if "'" != opening_single_quote:
            dynamic.append(('(\s|\A|[([{<]|")\'', '\\1' + opening_single_quote))  # opening single quote, even after (, {, <, [
        if '"' != double_prime:
            dynamic.append(('(\d)"', '\\1' + double_prime))  # 9" (double prime)
        if "'" != prime:
            dynamic.append(('(\d)\'', '\\1' + prime))  # 9' (prime)
        if "'" != apos:
            dynamic.append(('(\S)\'([^\'\s])', '\\1' + apos + '\\2'))  # apostrophe in a word
        if '"' != opening_quote:
            dynamic.append(('(\s|\A|[([{<])"(?!\s)', '\\1' + opening_quote))  # opening double quote, even after (, {, <, [
            # PHP: the original PHP regular expression had a problem, since there was only one capturing group, but both \1 and \2 were
            # used on the right-hand side. Since Python throws an exception in that case, while PHP simply treats \2 as an empty string,
            # I had to remove the "+'\\2'" after opening_quote.
        if '"' != closing_quote:
            dynamic.append(('"(\s|\S|\Z)', closing_quote + '\\1'))  # closing double quote
        if "'" != closing_single_quote:
            dynamic.append(('\'([\s.]|\Z)', closing_single_quote + '\\1'))  # closing single quote

        dynamic.append(('\b(\d+)x(\d+)\b', '\\1&#215;\\2'))  # 9x9 (times)

        self.dynamic = dynamic

    def __wptexturize_pushpop_element(self, text, stack, disabled_elements, opening='<', closing='>'):
        # Check if it is a closing tag -- otherwise assume opening tag
        if text[:2] != (opening + '/')[:2]:
            # Opening? Check text+1 against disabled elements
            matches = regex.match('^' + disabled_elements + '\b', text[1:])
            if matches is not None:
                # This disables texturize until we find a closing tag of our type
                # (e.g. <pre>) even if there was invalid nesting before that
                #
                # Example: in the case <pre>sadsadasd</code>"baba"</pre>
                #          "baba" won't be texturize
                stack.append(matches.group(0))
        else:
            # Closing? Check text+2 against disabled elements
            c = regex.escape(closing)
            matches = regex.match('^' + disabled_elements + c, text[2:])
            if matches is not None and len(stack) > 0:
                last = stack.pop()

                # Make sure it matches the opening tag
                if last != matches.group(0):
                    stack.append(last)

    def wptexturize(self, text):
        # Transform into regexp sub-expression used in _wptexturize_pushpop_element
        # Must do this every time in case plugins use these filters in a context sensitive manner
        no_texturize_tags = '(' + '|'.join(self.default_no_texturize_tags) + ')'
        no_texturize_shortcodes = '(' + '|'.join(self.default_no_texturize_shortcodes) + ')'

        no_texturize_tags_stack = []
        no_texturize_shortcodes_stack = []

        # PHP: Since Python doesn't support PHP's /U modifier (which inverts quantifier's greediness), I modified the regular expression accordingly
        textarr = regex.split('(<.*?>|\[.*?\])', text, flags=regex.DOTALL)

        result = []
        for curl in textarr:
            if len(curl) == 0:
                continue

            # Only call _wptexturize_pushpop_element if first char is correct tag opening
            first = curl[0]
            if '<' == first:
                self.__wptexturize_pushpop_element(curl, no_texturize_tags_stack, no_texturize_tags, '<', '>')
            elif '[' == first:
                self.__wptexturize_pushpop_element(curl, no_texturize_shortcodes_stack, no_texturize_shortcodes, '[', ']')
            elif len(no_texturize_shortcodes_stack) == 0 and len(no_texturize_tags_stack) == 0:
                # This is not a tag, nor is the texturization disabled static strings
                for search, replacement in self.static:
                    curl = curl.replace(search, replacement)
                # regular expressions
                for search, replacement in self.dynamic:
                    curl = regex.sub(search, replacement, curl)
            curl = regex.sub('&([^#])(?![a-zA-Z1-4]{1,8};)', '&#038;\\1', curl)
            result.append(curl)
        return ''.join(result)

    def __esc_attr(self, text):
        # safe_text = wp_check_invalid_utf8(text);
        # safe_text = _wp_specialchars(safe_text, ENT_QUOTES);
        return text  # apply_filters('attribute_escape', safe_text, text);

    def __translate_smiley(self, smiley):
        if len(smiley) == 0:
            return ''

        smiley = smiley.strip()
        img = self.wpsmiliestrans[smiley]
        smiley_masked = self.esc_attr(smiley)

        srcurl = "/images/smilies/" + img
        # srcurl = apply_filters('smilies_src', includes_url("images/smilies/' + img + '"), img, site_url());

        return " <img src='" + srcurl + "' alt='" + smiley_masked + "' class='wp-smiley' /> "

    def convert_smilies(self, text):
        if self.option_use_smilies and len(self.wp_smiliessearch) > 0:
            # HTML loop taken from texturize function, could possible be consolidated
            output = ''
            textarr = regex.split("(<.*?>)", text)  # capture the tags as well as in between
            for content in textarr:
                if (len(self.content) > 0) and ('<' != self.content[0]):  # If it's not a tag
                    content = php.preg_replace_callback(self.wp_smiliessearch, lambda x: self.translate_smiley(x), content)
                    pass
                output += content
        else:
            # return default text.
            output = text
        return output

    def __convert_chars_setup(self):
        # Translation of invalid Unicode references range to valid range
        self.wp_htmltranswinuni = {
            '&#128;': '&#8364;',  # the Euro sign
            '&#129;': '',
            '&#130;': '&#8218;',  # these are Windows CP1252 specific characters
            '&#131;': '&#402;',  # they would look weird on non-Windows browsers
            '&#132;': '&#8222;',
            '&#133;': '&#8230;',
            '&#134;': '&#8224;',
            '&#135;': '&#8225;',
            '&#136;': '&#710;',
            '&#137;': '&#8240;',
            '&#138;': '&#352;',
            '&#139;': '&#8249;',
            '&#140;': '&#338;',
            '&#141;': '',
            '&#142;': '&#381;',
            '&#143;': '',
            '&#144;': '',
            '&#145;': '&#8216;',
            '&#146;': '&#8217;',
            '&#147;': '&#8220;',
            '&#148;': '&#8221;',
            '&#149;': '&#8226;',
            '&#150;': '&#8211;',
            '&#151;': '&#8212;',
            '&#152;': '&#732;',
            '&#153;': '&#8482;',
            '&#154;': '&#353;',
            '&#155;': '&#8250;',
            '&#156;': '&#339;',
            '&#157;': '',
            '&#158;': '&#382;',
            '&#159;': '&#376;'
        }

    def convert_chars(self, content):
        # Remove metadata tags
        content = regex.sub('<title>(.+?)<\/title>', '', content)
        content = regex.sub('<category>(.+?)<\/category>', '', content)

        # Converts lone & characters into &#38; (a.k.a. &amp;)
        content = regex.sub('&([^#])(?![a-z1-4]{1,8};)', '&#038;\\1', content, regex.IGNORECASE)

        # Fix Word pasting
        for f, t in self.wp_htmltranswinuni.items():
            content = content.replace(f, t)

        # Just a little XHTML help
        content = content.replace('<br>', '<br/>')
        content = content.replace('<hr>', '<hr/>')
        return content

    def __autop_newline_preservation_helper(self, matches):
        return matches.group(0).replace("\n", "<WPPreserveNewline />")

    def wpautop(self, pee, br=True):
        pre_tags = dict()

        if pee.strip() == '':
            return ''

        pee = pee + "\n"  # just to make things a little easier, pad the end

        if pee.find('<pre') >= 0:
            pee_parts = pee.split('</pre>')
            last_pee = pee_parts.pop()
            pee = ''
            i = 0

            for pee_part in pee_parts:
                start = pee_part.find('<pre')

                # Malformed html?
                if start == -1:
                    pee += pee_part
                    continue

                name = "<pre wp-pre-tag-" + i + "></pre>"
                pre_tags[name] = pee_part[start:] + '</pre>'

                pee += pee_part[:start] + name
                i += 1

            pee += last_pee

        pee = regex.sub('<br />\s*<br />', "\n\n", pee)
        # Space things out a little
        self.allblocks = '(?:table|thead|tfoot|caption|col|colgroup|tbody|tr|td|th|div|dl|dd|dt|ul|ol|li|pre|select|option|form|map|area|blockquote|address|math|style|p|h[1-6]|hr|fieldset|noscript|legend|section|article|aside|hgroup|header|footer|nav|figure|figcaption|details|menu|summary)'
        pee = regex.sub('(<' + self.allblocks + '[^>]*>)', "\n\\1", pee)
        pee = regex.sub('(</' + self.allblocks + '>)', "\\1\n\n", pee)
        pee = pee.replace("\r\n", "\n").replace("\r", "\n")  # cross-platform newlines
        if pee.find('<object') >= 0:
            pee = regex.sub('\s*<param([^>]*)>\s*', "<param\\1>", pee)  # no pee inside object/embed
            pee = regex.sub('\s*</embed>\s*', '</embed>', pee)
        pee = regex.sub("\n\n+", "\n\n", pee)  # take care of duplicates
        # make paragraphs, including one at the end
        pees = regex.split('\n\s*\n', pee)
        pee = ''
        for trinkle in pees:
            if len(trinkle) > 0:  # PHP: this emulates PHP's flag PREG_SPLIT_NO_EMPTY for preg_split()
                pee += '<p>' + trinkle.strip("\n") + "</p>\n"
        pee = regex.sub('<p>\s*</p>', '', pee)  # under certain strange conditions it could create a P of entirely whitespace
        pee = regex.sub('<p>([^<]+)</(div|address|form)>', "<p>\\1</p></\\2>", pee)
        pee = regex.sub('<p>\s*(</?' + self.allblocks + '[^>]*>)\s*</p>', "\\1", pee)  # don't pee all over a tag
        pee = regex.sub("<p>(<li.+?)</p>", "\\1", pee)  # problem with nested lists
        pee = regex.sub('<p><blockquote([^>]*)>', "<blockquote\\1><p>", pee, regex.IGNORECASE)
        pee = pee.replace('</blockquote></p>', '</p></blockquote>')
        pee = regex.sub('<p>\s*(</?' + self.allblocks + '[^>]*>)', "\\1", pee)
        pee = regex.sub('(</?' + self.allblocks + '[^>]*>)\s*</p>', "\\1", pee)
        if br:
            pee = php.preg_replace_callback('<(script|style).*?<\/\\1>', lambda x: self.__autop_newline_preservation_helper(x), pee, regex.DOTALL)
            pee = regex.sub('(?<!<br />)\s*\n', "<br />\n", pee)  # optionally make line breaks
            pee = pee.replace('<WPPreserveNewline />', "\n")
        pee = regex.sub('(</?' + self.allblocks + '[^>]*>)\s*<br />', "\\1", pee)
        pee = regex.sub('<br />(\s*</?(?:p|li|div|dl|dd|dt|th|pre|td|ul|ol)[^>]*>)', '\\1', pee)
        pee = regex.sub("\n</p>$", '</p>', pee)

        if len(pre_tags) > 0:
            for f, t in pre_tags.items():
                pee = pee.replace(f, t)

        return pee

    def shortcode_unautop(self, pee):
        if len(self.shortcode_tags) == 0:
            return pee

        tagregexp = '|'.join([regex.escape(x) for x in self.shortcode_tags.keys()])

        pattern = (
            '<p>'                                 # Opening paragraph
            + '\\s*+'                             # Optional leading whitespace
            + '('                                 # 1: The shortcode
            +     '\\['                           # Opening bracket
            +     "(" + tagregexp + ")"           # 2: Shortcode name
            +     '(?![\\w-])'                    # Not followed by word character or hyphen
                                                  # Unroll the loop: Inside the opening shortcode tag
            +     '[^\\]/]*'                      # Not a closing bracket or forward slash
            +     '(?:'
            +         '/(?!\\])'                  # A forward slash not followed by a closing bracket
            +         '[^\\]/]*'                  # Not a closing bracket or forward slash
            +     ')*?'
            +     '(?:'
            +         '/\\]'                      # Self closing tag and closing bracket
            +     '|'
            +         '\\]'                       # Closing bracket
            +         '(?:'                       # Unroll the loop: Optionally, anything between the opening and closing shortcode tags
            +             '[^\\[]*+'              # Not an opening bracket
            +             '(?:'
            +                 '\\[(?!/\\2\\])'    # An opening bracket not followed by the closing shortcode tag
            +                 '[^\\[]*+'          # Not an opening bracket
            +             ')*+'
            +             '\\[/\\2\\]'            # Closing shortcode tag
            +         ')?'
            +     ')'
            + ')'
            + '\\s*+'                             # optional trailing whitespace
            + '</p>')                             # closing paragraph

        return regex.sub(pattern, '\\1', pee, regex.DOTALL | regex.VERSION1)
