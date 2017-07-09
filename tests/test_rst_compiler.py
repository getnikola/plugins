# coding: utf8
# Author: Rodrigo Bistolfi
# Date: 03/2013


""" Test cases for Nikola ReST extensions.
A base class ReSTExtensionTestCase provides the tests basic behaivor.
Subclasses must override the "sample" class attribute with the ReST markup.
The sample will be rendered as HTML using publish_parts() by setUp().
One method is provided for checking the resulting HTML:

    * assertHTMLContains(element, attributes=None, text=None)

The HTML is parsed with lxml for checking against the data you provide. The
method takes an element argument, a string representing the *name* of an HTML
tag, like "script" or "iframe". We will try to find this tag in the document
and perform the tests on it. You can pass a dictionary to the attributes kwarg
representing the name and the value of the tag attributes. The text kwarg takes
a string argument, which will be tested against the contents of the HTML
element.
One last caveat: you need to url unquote your urls if you are going to test
attributes like "src" or "link", since the HTML rendered by docutils will be
always unquoted.

"""


from __future__ import unicode_literals, absolute_import

import os
import sys

import io
try:
    from io import StringIO
except ImportError:
    from StringIO import StringIO  # NOQA
import tempfile

import docutils
from lxml import html
import pytest
import unittest

from nikola.nikola import Nikola
from nikola.post import Post
import nikola.plugins.compile.rest
from nikola.plugins.compile.rest import gist
from nikola.plugins.compile.rest import vimeo
import nikola.plugins.compile.rest.listing
from nikola.utils import _reload
from .base import BaseTestCase, FakeSite

if sys.version_info[0] == 3:
    import importlib.machinery
else:
    import imp

class ReSTExtensionTestCase(BaseTestCase):
    """ Base class for testing ReST extensions """

    sample = 'foo'
    deps = None
    extra_plugins_dirs = None

    def setUp(self):
        conf ={}
        if self.extra_plugins_dirs is not None:
            conf['EXTRA_PLUGINS_DIRS'] = self.extra_plugins_dirs
        self.site = Nikola(**conf)
        self.site.init_plugins()
        self.site.scan_posts()
        self.compiler = self.site.compilers['rest']
        return super(ReSTExtensionTestCase, self).setUp()

    def basic_test(self):
        """ Parse cls.sample into a HTML document tree """
        self.setHtmlFromRst(self.sample)

    def setHtmlFromRst(self, rst):
        """ Create html output from rst string """
        tmpdir = tempfile.mkdtemp()
        inf = os.path.join(tmpdir, 'inf')
        outf = os.path.join(tmpdir, 'outf')
        depf = os.path.join(tmpdir, 'outf.dep')
        with io.open(inf, 'w+', encoding='utf8') as f:
            f.write(rst)
        p = Post(inf, self.site.config, outf, False, None, '', self.compiler)
        self.site.post_per_input_file[inf] = p
        p.compile_html(inf, outf, post=p)
        with io.open(outf, 'r', encoding='utf8') as f:
            self.html = f.read()
        os.unlink(inf)
        os.unlink(outf)
        p.write_depfile(outf, p._depfile[outf])
        if os.path.isfile(depf):
            with io.open(depf, 'r', encoding='utf8') as f:
                self.assertEqual(self.deps.strip(), f.read().strip())
            os.unlink(depf)
        else:
            self.assertEqual(self.deps, None)
        os.rmdir(tmpdir)
        self.html_doc = html.parse(StringIO(self.html))

    def assertHTMLContains(self, element, attributes=None, text=None):
        """ Test if HTML document includes an element with the given
        attributes and text content

        """
        try:
            tag = next(self.html_doc.iter(element))
        except StopIteration:
            raise Exception("<{0}> not in {1}".format(element, self.html))
        else:
            if attributes:
                arg_attrs = set(attributes.items())
                tag_attrs = set(tag.items())
                self.assertTrue(arg_attrs.issubset(tag_attrs))
            if text:
                self.assertIn(text, tag.text)


class ReSTExtensionTestCaseTestCase(ReSTExtensionTestCase):
    """ Simple test for our base class :) """

    sample = '.. raw:: html\n\n   <iframe src="foo" height="bar">spam</iframe>'

    def test_test(self):
        self.basic_test()
        self.assertHTMLContains("iframe", attributes={"src": "foo"},
                                text="spam")
        self.assertRaises(Exception, self.assertHTMLContains, "eggs", {})


if __name__ == "__main__":
    unittest.main()
