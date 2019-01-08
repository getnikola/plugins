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

import datetime
import re

from docutils import languages, nodes, utils
from docutils.parsers.rst import Directive, directives, roles
from docutils.parsers.rst.directives.admonitions import BaseAdmonition
from docutils.parsers.rst.directives.body import MathBlock
from docutils.transforms import Transform

from nikola.plugin_categories import RestExtension
from nikola.plugins.compile.rest import add_node


class Plugin(RestExtension):

    name = "rest_sphinx_roles"

    def set_site(self, site):
        self.site = site
        roles.register_local_role("pep", pep_role)
        roles.register_local_role("rfc", rfc_role)
        roles.register_local_role("term", term_role)
        roles.register_local_role("option", option_role)
        roles.register_local_role("ref", ref_role)
        roles.register_local_role("eq", eq_role)

        # This is copied almost verbatim from Sphinx
        generic_docroles = {
            "command": nodes.strong,
            "dfn": nodes.emphasis,
            "envvar": nodes.literal,
            "kbd": nodes.literal,
            "mailheader": nodes.emphasis,
            "makevar": nodes.strong,
            "manpage": nodes.emphasis,
            "mimetype": nodes.emphasis,
            "newsgroup": nodes.emphasis,
            "program": nodes.strong,
            "regexp": nodes.literal,
        }

        for rolename, nodeclass in generic_docroles.items():
            generic = roles.GenericRole(rolename, nodeclass)
            role = roles.CustomRole(rolename, generic, {"classes": [rolename]})
            roles.register_local_role(rolename, role)

        specific_docroles = {
            "guilabel": menusel_role,
            "menuselection": menusel_role,
            "file": emph_literal_role,
            "samp": emph_literal_role,
            "abbr": abbr_role,
        }

        for rolename, func in specific_docroles.items():
            roles.register_local_role(rolename, func)

        # Handle abbr title
        add_node(abbreviation, visit_abbreviation, depart_abbreviation)

        for name, (base_url, prefix) in self.site.config.get("EXTLINKS", {}).items():
            roles.register_local_role(name, make_link_role(base_url, prefix))

        directives.register_directive("deprecated", VersionChange)
        directives.register_directive("versionadded", VersionChange)
        directives.register_directive("versionchanged", VersionChange)
        directives.register_directive("centered", Centered)
        directives.register_directive("hlist", HList)
        directives.register_directive("seealso", SeeAlso)
        directives.register_directive("glossary", Glossary)
        directives.register_directive("option", Option)
        directives.register_directive("math", Math)

        site.rst_transforms.append(Today)

        return super(Plugin, self).set_site(site)


# TODO: pep_role and rfc_role are similar enough that they
# should be a generic function called via partial


def pep_role(name, rawtext, text, lineno, inliner, options={}, content=[]):
    """Enhanced PEP role supporting anchors, for Sphinx compatibility."""
    anchor = ""
    anchorindex = text.find("#")
    if anchorindex > 0:
        text, anchor = text[:anchorindex], text[anchorindex:]
    try:
        pepnum = int(text)
    except ValueError:
        msg = inliner.reporter.error("invalid PEP number %s" % text, line=lineno)
        prb = inliner.problematic(rawtext, rawtext, msg)
        return [prb], [msg]
    ref = inliner.document.settings.pep_base_url + "pep-%04d" % pepnum
    sn = nodes.strong("PEP " + text, "PEP " + text)
    rn = nodes.reference("", "", internal=False, refuri=ref + anchor, classes=[name])
    rn += sn
    return [rn], []


explicit_title_re = re.compile(r"^(.+?)\s*(?<!\x00)<(.*?)>$", re.DOTALL)


def split_explicit_title(text):
    """Split role content into title and target, if given."""
    match = explicit_title_re.match(text)
    if match:
        return True, match.group(1), match.group(2)
    return False, text, text


def rfc_role(name, rawtext, text, lineno, inliner, options={}, content=[]):
    """Enhanced RFC role supporting anchors, for Sphinx compatibility."""
    anchor = ""
    anchorindex = text.find("#")
    if anchorindex > 0:
        text, anchor = text[:anchorindex], text[anchorindex:]
    try:
        rfcnum = int(text)
    except ValueError:
        msg = inliner.reporter.error("invalid PEP number %s" % text, line=lineno)
        prb = inliner.problematic(rawtext, rawtext, msg)
        return [prb], [msg]
    ref = inliner.document.settings.rfc_base_url + inliner.rfc_url % rfcnum
    sn = nodes.strong("RFC " + text, "RFC " + text)
    rn = nodes.reference("", "", internal=False, refuri=ref + anchor, classes=[name])
    rn += sn
    return [rn], []


# The code below is based in code from Sphinx

# Copyright (c) 2007-2013 by the Sphinx team (see AUTHORS file).
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:

# * Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.

# * Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


_litvar_re = re.compile("{([^}]+)}")


def emph_literal_role(typ, rawtext, text, lineno, inliner, options={}, content=[]):
    text = utils.unescape(text)
    pos = 0
    retnode = nodes.literal(role=typ.lower(), classes=[typ])
    for m in _litvar_re.finditer(text):
        if m.start() > pos:
            txt = text[pos : m.start()]
            retnode += nodes.Text(txt, txt)
        retnode += nodes.emphasis(m.group(1), m.group(1))
        pos = m.end()
    if pos < len(text):
        retnode += nodes.Text(text[pos:], text[pos:])
    return [retnode], []


_amp_re = re.compile(r"(?<!&)&(?![&\s])")


def menusel_role(typ, rawtext, text, lineno, inliner, options={}, content=[]):
    text = utils.unescape(text)
    if typ == "menuselection":
        text = text.replace("-->", u"\N{TRIANGULAR BULLET}")
    spans = _amp_re.split(text)

    node = nodes.emphasis(rawtext=rawtext)
    for i, span in enumerate(spans):
        span = span.replace("&&", "&")
        if i == 0:
            if len(span) > 0:
                textnode = nodes.Text(span)
                node += textnode
            continue
        accel_node = nodes.inline()
        letter_node = nodes.Text(span[0])
        accel_node += letter_node
        accel_node["classes"].append("accelerator")
        node += accel_node
        textnode = nodes.Text(span[1:])
        node += textnode

    node["classes"].append(typ)
    return [node], []


def make_link_role(base_url, prefix):
    def role(typ, rawtext, text, lineno, inliner, options={}, content=[]):
        text = utils.unescape(text)
        has_explicit_title, title, part = split_explicit_title(text)
        try:
            full_url = base_url % part
        except (TypeError, ValueError):
            inliner.reporter.warning(
                "unable to expand %s extlink with base URL %r, please make "
                "sure the base contains '%%s' exactly once" % (typ, base_url),
                line=lineno,
            )
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
    node.source, node.line = directive.state_machine.get_source_and_line(
        directive.lineno
    )


# FIXME: needs translations
versionlabels = {
    "versionadded": "New in version %s",
    "versionchanged": "Changed in version %s",
    "versionmodified": "Changed in version %s",
    "deprecated": "Deprecated since version %s",
}

math_option_spec = MathBlock.option_spec
math_option_spec["label"] = str


class Math(MathBlock):
    option_spec = math_option_spec

    def run(self):
        output = super(Math, self).run()
        if "label" in self.options and output:
            new_id = "eq-" + self.options["label"]
            output[0]["ids"].append(new_id)
        return output


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
        node["classes"] = ["versionadded"]
        node.document = self.state.document
        set_source_info(self, node)
        node["type"] = self.name
        node["version"] = self.arguments[0]
        text = versionlabels[self.name] % self.arguments[0]
        if len(self.arguments) == 2:
            inodes, messages = self.state.inline_text(
                self.arguments[1], self.lineno + 1
            )
            para = nodes.paragraph(self.arguments[1], "", *inodes)
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
                node[0].replace_self(nodes.paragraph("", "", content))
            node[0].insert(
                0, nodes.inline("", "%s: " % text, classes=["versionmodified"])
            )
        else:
            para = nodes.paragraph(
                "", "", nodes.inline("", "%s." % text, classes=["versionmodified"])
            )
            node.append(para)
        language = languages.get_language(
            self.state.document.settings.language_code, self.state.document.reporter
        )
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
        p_node["classes"] = ["centered"]
        strong_node = nodes.strong()
        inodes, messages = self.state.inline_text(self.arguments[0], self.lineno)
        strong_node.extend(inodes)
        p_node.children.append(strong_node)
        return [p_node] + messages


class HList(Directive):
    """
    Directive for a list that gets compacted horizontally.

    This differs from Sphinx's implementation in that it generates a table
    here at the directive level instead of creating a custom node and doing
    it on the writer.
    """

    has_content = True
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {"columns": int}

    def run(self):
        ncolumns = self.options.get("columns", 2)
        node = nodes.Element()
        node.document = self.state.document
        self.state.nested_parse(self.content, self.content_offset, node)
        if len(node.children) != 1 or not isinstance(
            node.children[0], nodes.bullet_list
        ):
            return [
                self.state.document.reporter.warning(
                    ".. hlist content is not a list", line=self.lineno
                )
            ]
        fulllist = node.children[0]
        # create a hlist node where the items are distributed
        npercol, nmore = divmod(len(fulllist), ncolumns)
        index = 0
        table = nodes.table()
        tg = nodes.tgroup()
        table += tg
        row = nodes.row()
        tbody = nodes.tbody()
        for column in range(ncolumns):
            endindex = index + (column < nmore and (npercol + 1) or npercol)
            colspec = nodes.colspec()
            colspec.attributes["stub"] = 0
            colspec.attributes["colwidth"] = 100.0 / ncolumns
            col = nodes.entry()
            col += nodes.bullet_list()
            col[0] += fulllist.children[index:endindex]
            index = endindex
            tg += colspec
            row += col
        tbody += row
        tg += tbody
        table["classes"].append("hlist")
        return [table]


class SeeAlso(BaseAdmonition):
    """
    An admonition mentioning things to look at as reference.
    """

    node_class = nodes.admonition

    def run(self):
        """Minor monkeypatch to set the title and classes right."""
        self.arguments = ["See also"]
        node_list = BaseAdmonition.run(self)
        node_list[0]["classes"] = ["admonition", "seealso"]
        return node_list


class Glossary(Directive):
    has_content = True

    def run(self):
        node = nodes.Element()
        node.document = self.state.document
        self.state.nested_parse(self.content, self.content_offset, node)
        node[0]["classes"] = ["glossary", "docutils"]
        # Set correct IDs for terms
        for term in node[0]:
            new_id = "term-" + nodes.make_id(term[0].astext())
            term[0]["ids"].append(new_id)
        return [node[0]]


def term_role(typ, rawtext, text, lineno, inliner, options={}, content=[]):
    # FIXME add stylable span inside link
    text = utils.unescape(text)
    target = "#term-" + nodes.make_id(text)
    pnode = nodes.reference(text, text, internal=True, refuri=target)
    pnode["classes"] = ["reference"]
    return [pnode], []


def eq_role(typ, rawtext, text, lineno, inliner, options={}, content=[]):
    # FIXME add stylable span inside link
    text = utils.unescape(text)
    target = "#eq-" + nodes.make_id(text)
    pnode = nodes.reference(text, text, internal=True, refuri=target)
    pnode["classes"] = ["reference"]
    return [pnode], []


class Option(Directive):
    has_content = True
    required_arguments = 1

    def run(self):
        refid = "cmdoption-arg-" + nodes.make_id(self.arguments[0])
        target = nodes.target(names=[refid], ids=[refid])
        dl = nodes.definition_list()
        dt = nodes.definition_list_item()
        term = nodes.term()
        term += nodes.literal(
            self.arguments[0], self.arguments[0], classes=["descname"]
        )
        dt += term
        definition = nodes.definition()
        dt += definition
        definition.document = self.state.document
        self.state.nested_parse(self.content, self.content_offset, definition)
        dl += dt
        return [target, dl]


def option_role(typ, rawtext, text, lineno, inliner, options={}, content=[]):
    # FIXME add stylable span inside link
    text = utils.unescape(text)
    target = "#cmdoption-arg-" + nodes.make_id(text)
    pnode = nodes.reference(text, text, internal=True, refuri=target)
    pnode["classes"] = ["reference"]
    return [pnode], []


_ref_re = re.compile("^(.*)<(.*)>$")


def ref_role(typ, rawtext, text, lineno, inliner, options={}, content=[]):
    """Reimplementation of Sphinx's ref role, but just links unconditionally."""

    msg_list = []
    match = _ref_re.match(text)
    if match is not None:
        text = match.groups()[0].strip()
        target = "#" + match.groups()[1]
        pnode = nodes.reference(text, text, internal=True, refuri=target)
    else:

        class RefVisitor(nodes.NodeVisitor, object):

            text = None

            def __init__(self, document, label):
                self._label = label
                super(RefVisitor, self).__init__(document)

            def visit_target(self, node):
                if self._label not in node.attributes["ids"]:
                    return
                else:
                    sibs = node.parent.children
                    next_sib = sibs[sibs.index(node) + 1]
                    # text has to be the figure caption
                    if isinstance(next_sib, nodes.figure):
                        self.text = [
                            x for x in next_sib.children if isinstance(x, nodes.caption)
                        ][0].astext()
                    elif isinstance(
                        next_sib, nodes.section
                    ):  # text has to be the title
                        self.text = next_sib.attributes["names"][0].title()

            def unknown_visit(self, node):
                pass

        visitor = RefVisitor(inliner.document, text)
        inliner.document.walk(visitor)
        if visitor.text is None:
            visitor.text = text.replace("-", " ").title()
            msg_list.append(
                inliner.reporter.warning(
                    'ref label {} is missing or not known yet at this point in the document or not immediately before figure or section. Proceeding anyway but title "{}" in this ref may be wrong.'.format(
                        text, visitor.text
                    )
                )
            )
        target = "#" + text
        pnode = nodes.reference(text, visitor.text, internal=True, refuri=target)
    pnode["classes"] = ["reference"]
    return [pnode], msg_list


_abbr_re = re.compile("\((.*)\)$", re.S)


class abbreviation(nodes.Inline, nodes.TextElement):
    """Node for abbreviations with explanations."""


def visit_abbreviation(self, node):
    attrs = {}
    if node.hasattr("explanation"):
        attrs["title"] = node["explanation"]
    self.body.append(self.starttag(node, "abbr", "", **attrs))


def depart_abbreviation(self, node):
    self.body.append("</abbr>")


def abbr_role(typ, rawtext, text, lineno, inliner, options={}, content=[]):

    text = utils.unescape(text)
    m = _abbr_re.search(text)
    if m is None:
        return [abbreviation(text, text)], []
    abbr = text[: m.start()].strip()
    expl = m.group(1)
    return [abbreviation(abbr, abbr, explanation=expl)], []


class Today(Transform):
    """
    Replace today with the date if it's not defined in the document.
    """

    # run before the default Substitutions
    default_priority = 210

    def apply(self, **kwargs):
        # only handle it if not otherwise defined in the document
        to_handle = set(["today"]) - set(self.document.substitution_defs)
        for ref in self.document.traverse(nodes.substitution_reference):
            refname = ref["refname"]
            if refname in to_handle:
                txt = datetime.datetime.today().strftime("%x")
                node = nodes.Text(txt, txt)
                ref.replace_self(node)
