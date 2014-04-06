# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

# This code is so you can run the samples without installing the package,
# and should be before any import touching nikola, in any file under tests/
import os
import sys
sys.path.append(os.path.join('v6', 'microdata'))

import unittest

from nikola.utils import LOGGER
import logbook
from .test_rst_compiler import ReSTExtensionTestCase


class ItemPropTestCase(ReSTExtensionTestCase):

    @staticmethod
    def setUpClass():
        LOGGER.notice('--- TESTS FOR ItemProp')
        LOGGER.level = logbook.WARNING

    @staticmethod
    def tearDownClass():
        sys.stdout.write('\n')
        LOGGER.level = logbook.NOTICE
        LOGGER.notice('--- END OF TESTS FOR ItemProp')

    def test_itemprop(self):
        # the result should be
        # <p><span itemprop="name">Test</span></p>
        self.sample = ':itemprop:`Test <name>`'
        self.basic_test()
        self.assertHTMLContains("span", attributes={"itemprop": "name"},
                                text="Test")
        self.assertHTMLContains("p")

    def test_itemprop_image(self):
        # the result should be
        # <img itemprop="photo" src="apple-pie.jpg" />
        self.sample = ":itemprop:`<photo|apple-pie.jpg|img>`"
        self.basic_test()
        self.assertHTMLContains("img", attributes={"itemprop": "photo", "src": "apple-pie.jpg"},
                                text="")
        self.assertHTMLContains("p")

    def test_itemprop_time(self):
        # the result should be
        # <time datetime="PT30M" itemprop="prepTime">30 min</time>
        self.sample = ":itemprop:`30 min <prepTime|PT30M|time>`"
        self.basic_test()
        self.assertHTMLContains("time", attributes={"itemprop": "prepTime", "datetime": "PT30M"},
                                text="30 min")
        self.assertHTMLContains("p")

    def test_itemprop_meta(self):
        # the result should be
        # <meta itemprop="datePublished" content="2009-05-08">May 8, 2009
        expected = (
            '<p>'
            '<meta content="2009-05-08" itemprop="datePublished" /> May 8, 2009'
            '</p>\n'
        )
        self.sample = ":itemprop:`<datePublished|2009-05-08|meta>` May 8, 2009"
        self.basic_test()
        self.assertHTMLContains("meta", attributes={"itemprop": "datePublished", "content": "2009-05-08"},
                                text="")
        self.assertHTMLContains("p")
        self.assertHTMLEqual(expected.strip())


class ItemPropUrlTestCase(ReSTExtensionTestCase):

    @staticmethod
    def setUpClass():
        LOGGER.notice('--- TESTS FOR ItemPropUrl')
        LOGGER.level = logbook.WARNING

    @staticmethod
    def tearDownClass():
        sys.stdout.write('\n')
        LOGGER.level = logbook.NOTICE
        LOGGER.notice('--- END OF TESTS FOR ItemPropUrl')

    def test_itemprop_url(self):
        # the result should be
        # <p><a href="http://somewhere/" itemprop="url">Test</a></p>
        self.sample = ':itemprop:`Test <url:http://somewhere/>`'
        self.basic_test()
        self.assertHTMLContains("a", attributes={"itemprop": "url", "href": "http://somewhere/"},
                                text="Test")
        self.assertHTMLContains("p")


class ItemScopeTestCase(ReSTExtensionTestCase):

    @staticmethod
    def setUpClass():
        LOGGER.notice('--- TESTS FOR ItemScope')
        LOGGER.level = logbook.WARNING

    @staticmethod
    def tearDownClass():
        sys.stdout.write('\n')
        LOGGER.level = logbook.NOTICE
        LOGGER.notice('--- END OF TESTS FOR ItemScope')

    def test_itemscope(self):
        # the result should be
        # <div itemscope itemtype="http://data-vocabulary.org/Person">
        # My name is John Doe
        # </div>
        self.sample = """.. itemscope:: Person

            My name is John Doe
        """
        self.basic_test()
        self.assertHTMLContains("div", attributes={"itemscope": "", "itemtype": "http://data-vocabulary.org/Person"},
                                text="My name is John Doe")

    def test_itemscope_class(self):
        # the result should be
        # <div itemscope itemtype="http://data-vocabulary.org/Person">
        # My name is John Doe
        # </div>
        self.sample = """.. itemscope:: Person
            :class: person-scope

            My name is John Doe
        """
        self.basic_test()
        self.assertHTMLContains("div", attributes={
                                "itemscope": "",
                                "class": "person-scope",
                                "itemtype": "http://data-vocabulary.org/Person"},
                                text="My name is John Doe")


class ItemScopePropTestCase(ReSTExtensionTestCase):

    @staticmethod
    def setUpClass():
        LOGGER.notice('--- TESTS FOR ItemScopeProp')
        LOGGER.level = logbook.WARNING

    @staticmethod
    def tearDownClass():
        sys.stdout.write('\n')
        LOGGER.level = logbook.NOTICE
        LOGGER.notice('--- END OF TESTS FOR ItemScopeProp')

    def test_itemscope_itemprop(self):
        # the result should be
        # <div itemscope itemtype="http://data-vocabulary.org/Person">
        # My name is <span itemprop="name">John Doe</span>
        # </div>
        self.sample = """.. itemscope:: Person

            My name is :itemprop:`John Doe <name>`
        """
        self.basic_test()
        self.assertHTMLContains("div", attributes={"itemscope": "", "itemtype": "http://data-vocabulary.org/Person"},
                                text="My name is ")
        self.assertHTMLContains("span", attributes={"itemprop": "name"},
                                text="John Doe")


class ItemScopeTagTestCase(ReSTExtensionTestCase):

    @staticmethod
    def setUpClass():
        LOGGER.notice('--- TESTS FOR ItemScopeTag')
        LOGGER.level = logbook.WARNING

    @staticmethod
    def tearDownClass():
        sys.stdout.write('\n')
        LOGGER.level = logbook.NOTICE
        LOGGER.notice('--- END OF TESTS FOR ItemScopeTag')

    def test_itemscope_tag(self):
        # the result should be
        # <p itemscope itemtype="http://data-vocabulary.org/Person">
        # My name is <span itemprop="name">John Doe</span>
        # </p>
        self.sample = """.. itemscope:: Person
            :tag: p

            My name is :itemprop:`John Doe <name>`
        """
        self.basic_test()
        self.assertHTMLContains("p", attributes={"itemscope": "", "itemtype": "http://data-vocabulary.org/Person"},
                                text="My name is ")
        self.assertHTMLContains("span", attributes={"itemprop": "name"},
                                text="John Doe")

    def test_itemscope_tag_span(self):
        # the result should be
        # <span itemprop="ingredient" itemscope itemtype="http://data-vocabulary.org/RecipeIngredient">
        #  Thinly-sliced <span itemprop="name">apples</span>:<span itemprop="amount">6 cups</span>
        # </span>
        expected = (
            '<span itemprop="ingredient" itemscope itemtype="http://data-vocabulary.org/RecipeIngredient">'
            'Thinly-sliced <span itemprop="name">apples</span>:'
            '<span itemprop="amount">6 cups</span>'
            '</span>'
        )
        self.sample = """.. itemscope:: RecipeIngredient
            :tag: span
            :itemprop: ingredient

            Thinly-sliced :itemprop:`apples <name>`::itemprop:`6 cups <amount>`
        """
        self.basic_test()
        self.assertHTMLEqual(expected.strip())


class ItemPropBlockTestCase(ReSTExtensionTestCase):

    @staticmethod
    def setUpClass():
        LOGGER.notice('--- TESTS FOR ItemPropBlock')
        LOGGER.level = logbook.WARNING

    @staticmethod
    def tearDownClass():
        sys.stdout.write('\n')
        LOGGER.level = logbook.NOTICE
        LOGGER.notice('--- END OF TESTS FOR ItemPropBlock')

    def test_itempropblock_h1(self):
        # the result should be
        # <div itemscope itemtype="http://data-vocabulary.org/Recipe">
        # <h1 itemprop="name">Grandma\'s Holiday Apple Pie</h1>
        # </div>
        self.sample = """.. itemscope:: Recipe

            .. itempropblock:: name
                :tag: h1

                Grandma's Holiday Apple Pie
        """
        self.basic_test()
        self.assertHTMLContains("div", attributes={"itemscope": "", "itemtype": "http://data-vocabulary.org/Recipe"},
                                text="")
        self.assertHTMLContains("h1", attributes={"itemprop": "name"},
                                text="Grandma's Holiday Apple Pie")

    def test_itempropblock_class(self):
        # the result should be
        # <div itemscope itemtype="http://data-vocabulary.org/Recipe">
        # <h1 itemprop="name">Grandma\'s Holiday Apple Pie</h1>
        # </div>
        self.sample = """.. itemscope:: Recipe

            .. itempropblock:: name
                :tag: h1
                :class: recipe-title

                Grandma's Holiday Apple Pie
        """
        self.basic_test()
        self.assertHTMLContains("div", attributes={"itemscope": "", "itemtype": "http://data-vocabulary.org/Recipe"},
                                text="")
        self.assertHTMLContains("h1", attributes={"itemprop": "name",
                                "class": "recipe-title"},
                                text="Grandma's Holiday Apple Pie")

    def test_itempropblock_nested(self):
        # the result should be
        # <div itemscope itemtype="http://data-vocabulary.org/Recipe">
        # <div itemprop="instructions">
        # <p itemprop="instruction">Cut and peel apples.</p>
        # <p itemprop="instruction">Mix sugar and cinnamon. Use additional sugar for tart apples.</p>
        # </div></div>
        expected = (
            '<div itemscope itemtype="http://data-vocabulary.org/Recipe">'
            '<div itemprop="instructions">'
            '<p itemprop="instruction">Cut and peel apples.</p>'
            '<p itemprop="instruction">Mix sugar and cinnamon. Use additional sugar for tart apples.</p>'
            '</div></div>'
        )
        self.sample = """.. itemscope:: Recipe

            .. itempropblock:: instructions

                .. itempropblock:: instruction
                    :tag: p

                    Cut and peel apples.

                .. itempropblock:: instruction
                    :tag: p

                    Mix sugar and cinnamon. Use additional sugar for tart apples.
        """
        self.basic_test()
        self.assertHTMLEqual(expected.strip())


class ItemScopeNestedTestCase(ReSTExtensionTestCase):

    @staticmethod
    def setUpClass():
        LOGGER.notice('--- TESTS FOR ItemScopeNested')
        LOGGER.level = logbook.WARNING

    @staticmethod
    def tearDownClass():
        sys.stdout.write('\n')
        LOGGER.level = logbook.NOTICE
        LOGGER.notice('--- END OF TESTS FOR ItemScopeNested')

    def test_nested_scope(self):
        # the result should be
        # <div itemscope itemtype="http://data-vocabulary.org/Person">
        # <p>My name is <span itemprop="name">John Doe</span></p>
        # <p itemprop="address" itemscope itemtype="http://data-vocabulary.org/Address">
        # My name is <span itemprop="name">John Doe</span>
        # </p></div>
        expected = (
            '<div itemscope itemtype="http://data-vocabulary.org/Person">'
            '<p>'
            'My name is <span itemprop="name">John Doe</span>'
            '</p>'
            '<p itemprop="address" itemscope itemtype="http://data-vocabulary.org/Address">'
            'My name is <span itemprop="name">John Doe</span>'
            '</p>'
            '</div>'
        )
        self.sample = """.. itemscope:: Person

            My name is :itemprop:`John Doe <name>`

            .. itemscope:: Address
                :tag: p
                :itemprop: address

                My name is :itemprop:`John Doe <name>`
        """
        self.basic_test()
        self.assertHTMLContains("div", attributes={"itemscope": "",
                                "itemtype": "http://data-vocabulary.org/Person"},
                                text="")
        self.assertHTMLEqual(expected.strip())


class ItemScopeNestedCompactTestCase(ReSTExtensionTestCase):

    @staticmethod
    def setUpClass():
        LOGGER.notice('--- TESTS FOR ItemScopeNestedCompact')
        LOGGER.level = logbook.WARNING

    @staticmethod
    def tearDownClass():
        sys.stdout.write('\n')
        LOGGER.level = logbook.NOTICE
        LOGGER.notice('--- END OF TESTS FOR ItemScopeNestedCompact')

    def test_nested_scope_compact(self):
        # the result should be
        # <p itemscope itemtype="http://data-vocabulary.org/Person">
        # My name is <span itemprop="name">John Doe</span>
        # <span itemprop="address" itemscope itemtype="http://data-vocabulary.org/Address">
        # My name is <span itemprop="name">John Doe</span>
        # </span></p>
        expected = (
            '<p itemscope itemtype="http://data-vocabulary.org/Person">'
            'My name is <span itemprop="name">John Doe</span>'
            '<span itemprop="address" itemscope itemtype="http://data-vocabulary.org/Address">'
            'My name is <span itemprop="name">John Doe</span>'
            '</span>'
            '</p>'
        )
        self.sample = """.. itemscope:: Person
            :tag: p
            :compact:

            My name is :itemprop:`John Doe <name>`

            .. itemscope:: Address
                :tag: span
                :itemprop: address

                My name is :itemprop:`John Doe <name>`
        """
        self.basic_test()
        self.assertHTMLContains("p", attributes={"itemscope": "",
                                "itemtype": "http://data-vocabulary.org/Person"},
                                text="My name is ")
        self.assertHTMLEqual(expected.strip())


if __name__ == "__main__":
    unittest.main()
