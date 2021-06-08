# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from pytest import fixture

from . import V7_PLUGIN_PATH


def test_itemprop(do_test):
    assert do_test("""\
        :itemprop:`Test <name>`
    """) == (
        '<p><span itemprop="name">Test</span></p>'
    )


def test_itemprop_image(do_test):
    assert do_test("""\
        :itemprop:`<photo|apple-pie.jpg|img>`
    """) == (
        '<p><img itemprop="photo" src="apple-pie.jpg" /></p>'
    )


def test_itemprop_time(do_test):
    assert do_test("""\
        :itemprop:`30 min <prepTime|PT30M|time>`
    """) == (
        '<p><time datetime="PT30M" itemprop="prepTime">30 min</time></p>'
    )


def test_itemprop_meta(do_test):
    assert do_test("""\
        :itemprop:`<datePublished|2009-05-08|meta>` May 8, 2009
    """) == (
        '<p><meta content="2009-05-08" itemprop="datePublished" /> May 8, 2009</p>'
    )


def test_itemprop_url(do_test):
    assert do_test("""\
        :itemprop:`Test <url:http://somewhere/>`
    """) == (
        '<p><a href="http://somewhere/" itemprop="url">Test</a></p>'
    )


def test_itemscope(do_test):
    assert do_test("""\
        .. itemscope:: Person
    
            My name is John Doe
    """) == (
        '<div itemscope="True" itemtype="http://schema.org/Person">'
        '<p>My name is John Doe</p>'
        '</div>'
    )


def test_itemscope_class(do_test):
    assert do_test("""\
        .. itemscope:: Person
            :class: person-scope
    
            My name is John Doe
    """) == (
        '<div class="person-scope" itemscope="True" itemtype="http://schema.org/Person">'
        '<p>My name is John Doe</p>'
        '</div>'
    )


def test_itemscope_itemprop(do_test):
    assert do_test("""\
        .. itemscope:: Person

            My name is :itemprop:`John Doe <name>`
    """) == (
        '<div itemscope="True" itemtype="http://schema.org/Person">'
        '<p>My name is <span itemprop="name">John Doe</span></p>'
        '</div>'
    )


def test_itemscope_tag_p(do_test):
    assert do_test("""\
        .. itemscope:: Person
            :tag: p
    
            My name is :itemprop:`John Doe <name>`
    """) == (
        '<p itemscope="True" itemtype="http://schema.org/Person">'
        '<p>My name is <span itemprop="name">John Doe</span></p>'
        '</p>'
    )


def test_itemscope_tag_span(do_test):
    assert do_test("""\
        .. itemscope:: RecipeIngredient
            :tag: span
            :itemprop: ingredient
    
            Thinly-sliced :itemprop:`apples <name>`::itemprop:`6 cups <amount>`
    """) == (
        '<span itemprop="ingredient" itemscope="True" itemtype="http://schema.org/RecipeIngredient">'
        '<p>Thinly-sliced <span itemprop="name">apples</span>:<span itemprop="amount">6 cups</span></p>'
        '</span>'
    )


def test_itempropblock_h1(do_test):
    assert do_test("""\
        .. itemscope:: Recipe
    
            .. itempropblock:: name
                :tag: h1
    
                Holiday Apple Pie
    """) == (
        '<div itemscope="True" itemtype="http://schema.org/Recipe">'
        '<h1 itemprop="name"><p>Holiday Apple Pie</p></h1>'
        '</div>'
    )


def test_itempropblock_class(do_test):
    assert do_test("""\
        .. itemscope:: Recipe
        
            .. itempropblock:: name
                :tag: h1
                :class: recipe-title
    
                Holiday Apple Pie
    """) == (
        '<div itemscope="True" itemtype="http://schema.org/Recipe">'
        '<h1 class="recipe-title" itemprop="name"><p>Holiday Apple Pie</p></h1>'
        '</div>'
    )


def test_itempropblock_nested(do_test):
    assert do_test("""\
        .. itemscope:: Recipe

            .. itempropblock:: instructions
        
                .. itempropblock:: instruction
                    :tag: p
        
                    Cut and peel apples.
        
                .. itempropblock:: instruction
                    :tag: p
        
                    Mix sugar and cinnamon. Use additional sugar for tart apples.
    """) == (
        '<div itemscope="True" itemtype="http://schema.org/Recipe">'
        '<div itemprop="instructions">'
        '<p itemprop="instruction"><p>Cut and peel apples.</p></p>'
        '<p itemprop="instruction"><p>Mix sugar and cinnamon. Use additional sugar for tart apples.</p></p>'
        '</div>'
        '</div>'
    )


def test_nested_scope(do_test):
    assert do_test("""\
        .. itemscope:: Person
    
            My name is :itemprop:`John Doe <name>`
    
            .. itemscope:: Address
                :tag: p
                :itemprop: address
    
                My name is :itemprop:`John Doe <name>`
    """) == (
        '<div itemscope="True" itemtype="http://schema.org/Person">'
        '<p>My name is <span itemprop="name">John Doe</span></p>'
        '<p itemprop="address" itemscope="True" itemtype="http://schema.org/Address">'
        '<p>My name is <span itemprop="name">John Doe</span></p>'
        '</p>'
        '</div>'
    )


def test_nested_scope_compact(do_test):
    assert do_test("""\
       .. itemscope:: Person
            :tag: p
            :compact:
    
            My name is :itemprop:`John Doe <name>`
    
            .. itemscope:: Address
                :tag: span
                :itemprop: address
    
                My name is :itemprop:`John Doe <name>`
    """) == (
        '<p itemscope="True" itemtype="http://schema.org/Person">'
        '<p>My name is <span itemprop="name">John Doe</span></p>'
        '<span itemprop="address" itemscope="True" itemtype="http://schema.org/Address">'
        '<p>My name is <span itemprop="name">John Doe</span></p>'
        '</span>'
        '</p>'
    )


@fixture
def do_test(basic_compile_test):
    def f(data: str) -> str:
        return basic_compile_test('.rst', data, extra_plugins_dirs=[V7_PLUGIN_PATH / 'microdata']).raw_html.replace('\n', '')

    return f
