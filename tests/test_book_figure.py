# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pytest import fixture

from . import CompileResult, V7_PLUGIN_PATH


def test_default(do_test):
    compile_result = do_test('.. book_figure:: Get Nikola')

    assert compile_result.raw_html.replace('\n', '') == (
        '<div class="">'
        '<div class="book-figure-content">'
        '<p class="book-figure-title">Get Nikola</p>'
        '</div></div>'
    )


def test_full_02(do_test):
    compile_result = do_test("""\
        .. book_figure:: Get Nikola
            :class: book-figure
            :url: http://getnikola.com/
            :author: Roberto Alsina
            :isbn_13: 1234567890123
            :isbn_10: 1234567890
            :asin: B001234567
            :image_url: http://getnikola.com/galleries/demo/tesla2_lg.jpg

            Your review.
    """)

    assert compile_result.raw_html.replace('\n', '') == (
        '<div class="book-figure">'
        '<div class="book-figure-media">'
        '<a class="book-figure-image" href="http://getnikola.com/" target="_blank">'
        '<img src="http://getnikola.com/galleries/demo/tesla2_lg.jpg" alt="Get Nikola" />'
        '</a></div>'
        '<div class="book-figure-content">'
        '<a class="book-figure-title" href="http://getnikola.com/" target="_blank">Get Nikola</a>'
        '<p class="book-figure-author">by Roberto Alsina</p>'
        '<table class="book-figure-book-number">'
        '<tbody>'
        '<tr><th>ISBN-13:</th><td>1234567890123</td></tr>'
        '<tr><th>ISBN-10:</th><td>1234567890</td></tr>'
        '<tr><th>ASIN:</th><td>B001234567</td></tr>'
        '</tbody></table>'
        '<div class="book-figure-review">'
        '<p>Your review.</p>'
        '</div></div></div>'
    )


def test_with_author_url(do_test):
    compile_result = do_test("""\
        .. book_figure:: Get Nikola
            :class: book-figure
            :url: http://getnikola.com/
            :author: Roberto Alsina
            :author_url: http://ralsina.me/
            :isbn_13: 1234567890123
            :isbn_10: 1234567890
            :asin: B001234567
            :image_url: http://getnikola.com/galleries/demo/tesla2_lg.jpg

            Your review.
    """)

    assert compile_result.raw_html.replace('\n', '') == (
        '<div class="book-figure">'
        '<div class="book-figure-media">'
        '<a class="book-figure-image" href="http://getnikola.com/" target="_blank">'
        '<img src="http://getnikola.com/galleries/demo/tesla2_lg.jpg" alt="Get Nikola" />'
        '</a></div>'
        '<div class="book-figure-content">'
        '<a class="book-figure-title" href="http://getnikola.com/" target="_blank">Get Nikola</a>'
        '<p class="book-figure-author">by <a href="http://ralsina.me/" target="_blank">Roberto Alsina</a></p>'
        '<table class="book-figure-book-number">'
        '<tbody>'
        '<tr><th>ISBN-13:</th><td>1234567890123</td></tr>'
        '<tr><th>ISBN-10:</th><td>1234567890</td></tr>'
        '<tr><th>ASIN:</th><td>B001234567</td></tr>'
        '</tbody></table>'
        '<div class="book-figure-review">'
        '<p>Your review.</p>'
        '</div></div></div>'
    )


@fixture
def do_test(basic_compile_test):
    def f(data: str) -> CompileResult:
        return basic_compile_test('.rst', data, extra_plugins_dirs=[V7_PLUGIN_PATH / 'book_figure'])

    return f
