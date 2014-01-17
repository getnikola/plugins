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

# This code is so you can run the samples without installing the package,
# and should be before any import touching nikola, in any file under tests/
import os
import sys
extra_plugin_dir = os.path.join(os.path.dirname(__file__), '..')
#extra_plugin_dir = 'plugins'
sys.path.insert(0, extra_plugin_dir)


import codecs
try:
    from io import StringIO
except ImportError:
    from StringIO import StringIO  # NOQA
import tempfile

from lxml import html
import unittest
from yapsy.PluginManager import PluginManager

from nikola import utils
import nikola.plugins.compile.rest
import nikola.plugins.compile.rest.listing
from nikola.utils import STDERR_HANDLER
from nikola.utils import LOGGER
from nikola.plugin_categories import (
    Command,
    Task,
    LateTask,
    TemplateSystem,
    PageCompiler,
    TaskMultiplier,
    RestExtension,
)
from .test_base import BaseTestCase


class FakePost(object):

    def __init__(self, title, slug):
        self._title = title
        self._slug = slug
        self._meta = {'slug': slug}

    def title(self):
        return self._title

    def meta(self, key):
        return self._meta[key]

    def permalink(self):
        return '/posts/' + self._slug


class FakeSite(object):
    def __init__(self):
        self.template_system = self
        self.config = {
            'DISABLED_PLUGINS': [],
            'EXTRA_PLUGINS': [],
            'DEFAULT_LANG': 'en',
            'EXTRA_PLUGINS_DIRS': [extra_plugin_dir],
        }
        self.EXTRA_PLUGINS = self.config['EXTRA_PLUGINS']
        self.plugin_manager = PluginManager(categories_filter={
            "Command": Command,
            "Task": Task,
            "LateTask": LateTask,
            "TemplateSystem": TemplateSystem,
            "PageCompiler": PageCompiler,
            "TaskMultiplier": TaskMultiplier,
            "RestExtension": RestExtension,
        })
        self.loghandlers = [STDERR_HANDLER]
        self.plugin_manager.setPluginInfoExtension('plugin')
        extra_plugins_dirs = self.config['EXTRA_PLUGINS_DIRS']
        LOGGER.notice('--- %s' % extra_plugins_dirs)
        if sys.version_info[0] == 3:
            places = [
                os.path.join(os.path.dirname(utils.__file__), 'plugins'),
            ] + [path for path in extra_plugins_dirs if path]
        else:
            places = [
                os.path.join(os.path.dirname(utils.__file__), utils.sys_encode('plugins')),
            ] + [utils.sys_encode(path) for path in extra_plugins_dirs if path]
        self.plugin_manager.setPluginPlaces(places)
        self.plugin_manager.collectPlugins()

        self.timeline = [
            FakePost(title='Fake post',
                     slug='fake-post')
        ]

    def render_template(self, name, _, context):
        return('<img src="IMG.jpg">')


class ReSTExtensionTestCase(BaseTestCase):
    """ Base class for testing ReST extensions """

    sample = 'foo'
    deps = None

    def setUp(self):
        self.compiler = nikola.plugins.compile.rest.CompileRest()
        self.compiler.set_site(FakeSite())
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
        with codecs.open(inf, 'wb+', 'utf8') as f:
            f.write(rst)
        self.html = self.compiler.compile_html(inf, outf)
        with codecs.open(outf, 'r', 'utf8') as f:
            self.html = f.read()
        os.unlink(inf)
        os.unlink(outf)
        if os.path.isfile(depf):
            with codecs.open(depf, 'r', 'utf8') as f:
                self.assertEqual(self.deps, f.read())
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

    def assertHTMLEqual(self, html):
        """ Test if HTML document is the same
        """
        html_string = self.html.strip().replace('\n', '')
        self.assertEqual(html_string, html)


class ReSTExtensionTestCaseTestCase(ReSTExtensionTestCase):
    """ Simple test for our base class :) """

    sample = '.. raw:: html\n\n   <iframe src="foo" height="bar">spam</iframe>'

    def test_test(self):
        self.basic_test()
        self.assertHTMLContains("iframe", attributes={"src": "foo"},
                                text="spam")
        self.assertRaises(Exception, self.assertHTMLContains, "eggs", {})
