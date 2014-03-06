# -*- coding: utf-8 -*-

# Copyright © 2012-2013 Roberto Alsina and others.

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

import re

from docutils import nodes, utils
from docutils.parsers.rst import Directive, directives, roles
from docutils import languages

from nikola.plugin_categories import RestExtension


class Plugin(RestExtension):

    name = "rest_sphinx_roles"

    def set_site(self, site):
        self.site = site
        roles.register_local_role('pep', pep_role)
        roles.register_local_role('rfc', rfc_role)

        # This is copied almost verbatim from Sphinx
        generic_docroles = {
            'command': nodes.strong,
            'dfn': nodes.emphasis,
            'kbd': nodes.literal,
            'mailheader': nodes.emphasis,
            'makevar': nodes.strong,
            'manpage': nodes.emphasis,
            'mimetype': nodes.emphasis,
            'newsgroup': nodes.emphasis,
            'program': nodes.strong,
            'regexp': nodes.literal,
        }

        for rolename, nodeclass in generic_docroles.items():
            generic = roles.GenericRole(rolename, nodeclass)
            role = roles.CustomRole(rolename, generic, {'classes': [rolename]})
            roles.register_local_role(rolename, role)

        specific_docroles = {
            'guilabel': menusel_role,
            'menuselection': menusel_role,
            'file': emph_literal_role,
            'samp': emph_literal_role,
        }

        for rolename, func in specific_docroles.items():
            roles.register_local_role(rolename, func)

        for name, (base_url, prefix) in self.site.config.get('EXTLINKS', {}).items():
            roles.register_local_role(name, make_link_role(base_url, prefix))

        directives.register_directive('deprecated', VersionChange)
        directives.register_directive('versionadded', VersionChange)
        directives.register_directive('versionchanged', VersionChange)
        directives.register_directive('centered', Centered)

        return super(Plugin, self).set_site(site)

# TODO: pep_role and rfc_role are similar enough that they
# should be a generic function called via partial


def pep_role(name, rawtext, text, lineno, inliner, options={}, content=[]):
    """Enhanced PEP role supporting anchors, for Sphinx compatibility."""
    anchor = ''
    anchorindex = text.find('#')
    if anchorindex > 0:
        text, anchor = text[:anchorindex], text[anchorindex:]
    try:
        pepnum = int(text)
    except ValueError:
        msg = inliner.reporter.error('invalid PEP number %s' % text, line=lineno)
        prb = inliner.problematic(rawtext, rawtext, msg)
        return [prb], [msg]
    ref = inliner.document.settings.pep_base_url + 'pep-%04d' % pepnum
    sn = nodes.strong('PEP ' + text, 'PEP ' + text)
    rn = nodes.reference('', '', internal=False, refuri=ref + anchor,
                         classes=[name])
    rn += sn
    return [rn], []

explicit_title_re = re.compile(r'^(.+?)\s*(?<!\x00)<(.*?)>$', re.DOTALL)


def split_explicit_title(text):
    """Split role content into title and target, if given."""
    match = explicit_title_re.match(text)
    if match:
        return True, match.group(1), match.group(2)
    return False, text, text


def rfc_role(name, rawtext, text, lineno, inliner, options={}, content=[]):
    """Enhanced RFC role supporting anchors, for Sphinx compatibility."""
    anchor = ''
    anchorindex = text.find('#')
    if anchorindex > 0:
        text, anchor = text[:anchorindex], text[anchorindex:]
    try:
        rfcnum = int(text)
    except ValueError:
        msg = inliner.reporter.error('invalid PEP number %s' % text, line=lineno)
        prb = inliner.problematic(rawtext, rawtext, msg)
        return [prb], [msg]
    ref = inliner.document.settings.rfc_base_url + inliner.rfc_url % rfcnum
    sn = nodes.strong('RFC ' + text, 'RFC ' + text)
    rn = nodes.reference('', '', internal=False, refuri=ref + anchor,
                         classes=[name])
    rn += sn
    return [rn], []

# The code below is copied verbatim from Sphinx

#Copyright (c) 2007-2013 by the Sphinx team (see AUTHORS file).
#All rights reserved.

#Redistribution and use in source and binary forms, with or without
#modification, are permitted provided that the following conditions are
#met:

#* Redistributions of source code must retain the above copyright
  #notice, this list of conditions and the following disclaimer.

#* Redistributions in binary form must reproduce the above copyright
  #notice, this list of conditions and the following disclaimer in the
  #documentation and/or other materials provided with the distribution.

#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
#A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
#OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
#DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
#THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

_litvar_re = re.compile('{([^}]+)}')


def emph_literal_role(typ, rawtext, text, lineno, inliner,
                      options={}, content=[]):
    text = utils.unescape(text)
    pos = 0
    retnode = nodes.literal(role=typ.lower(), classes=[typ])
    for m in _litvar_re.finditer(text):
        if m.start() > pos:
            txt = text[pos:m.start()]
            retnode += nodes.Text(txt, txt)
        retnode += nodes.emphasis(m.group(1), m.group(1))
        pos = m.end()
    if pos < len(text):
        retnode += nodes.Text(text[pos:], text[pos:])
    return [retnode], []

_amp_re = re.compile(r'(?<!&)&(?![&\s])')


def menusel_role(typ, rawtext, text, lineno, inliner, options={}, content=[]):
    text = utils.unescape(text)
    if typ == 'menuselection':
        text = text.replace('-->', u'\N{TRIANGULAR BULLET}')
    spans = _amp_re.split(text)

    node = nodes.emphasis(rawtext=rawtext)
    for i, span in enumerate(spans):
        span = span.replace('&&', '&')
        if i == 0:
            if len(span) > 0:
                textnode = nodes.Text(span)
                node += textnode
            continue
        accel_node = nodes.inline()
        letter_node = nodes.Text(span[0])
        accel_node += letter_node
        accel_node['classes'].append('accelerator')
        node += accel_node
        textnode = nodes.Text(span[1:])
        node += textnode

    node['classes'].append(typ)
    return [node], []


def make_link_role(base_url, prefix):
    def role(typ, rawtext, text, lineno, inliner, options={}, content=[]):
        text = utils.unescape(text)
        has_explicit_title, title, part = split_explicit_title(text)
        try:
            full_url = base_url % part
        except (TypeError, ValueError):
            inliner.reporter.warning(
                'unable to expand %s extlink with base URL %r, please make '
                'sure the base contains \'%%s\' exactly once'
                % (typ, base_url), line=lineno)
            full_url = base_url + part
        if not has_explicit_title:
            if prefix is None:
                title = full_url
            else:
                title = prefix + part
        pnode = nodes.reference(title, title, internal=False, refuri=full_url)
        return [pnode], []
    return role


def set_source_info(directive, node):
    node.source, node.line = \
        directive.state_machine.get_source_and_line(directive.lineno)

# FIXME: needs translations
versionlabels = {
    'versionadded': 'New in version %s',
    'versionchanged': 'Changed in version %s',
    'versionmodified': 'Changed in version %s',
    'deprecated': 'Deprecated since version %s',
}


class VersionChange(Directive):
    """
    Directive to describe a change/addition/deprecation in a specific version.
    """
    has_content = True
    required_arguments = 1
    optional_arguments = 1
    final_argument_whitespace = True
    option_spec = {}

    def run(self):
        node = nodes.paragraph()
        node['classes'] = ['versionadded']
        node.document = self.state.document
        set_source_info(self, node)
        node['type'] = self.name
        node['version'] = self.arguments[0]
        text = versionlabels[self.name] % self.arguments[0]
        if len(self.arguments) == 2:
            inodes, messages = self.state.inline_text(self.arguments[1],
                                                      self.lineno + 1)
            para = nodes.paragraph(self.arguments[1], '', *inodes)
            set_source_info(self, para)
            node.append(para)
        else:
            messages = []
        if self.content:
            self.state.nested_parse(self.content, self.content_offset, node)
        if len(node):
            if isinstance(node[0], nodes.paragraph) and node[0].rawsource:
                content = nodes.inline(node[0].rawsource, translatable=True)
                content.source = node[0].source
                content.line = node[0].line
                content += node[0].children
                node[0].replace_self(nodes.paragraph('', '', content))
            node[0].insert(0, nodes.inline('', '%s: ' % text,
                                           classes=['versionmodified']))
        else:
            para = nodes.paragraph('', '', nodes.inline('', '%s.' % text, classes=['versionmodified']))
            node.append(para)
        language = languages.get_language(self.state.document.settings.language_code,
                                          self.state.document.reporter)
        language.labels.update(versionlabels)
        return [node] + messages


class Centered(Directive):
    """
    Directive to create a centered line of bold text.
    """
    has_content = False
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = {}

    def run(self):
        if not self.arguments:
            return []
        p_node = nodes.paragraph()
        p_node['classes'] = ['centered']
        strong_node = nodes.strong()
        inodes, messages = self.state.inline_text(self.arguments[0],
                                                  self.lineno)
        strong_node.extend(inodes)
        p_node.children.append(strong_node)
        return [p_node] + messages
