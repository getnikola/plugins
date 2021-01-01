# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pytest import fixture

from . import CompileResult, V7_PLUGIN_PATH


def test_default(do_test):
    compile_result = do_test('.. link_figure:: http://getnikola.com/')

    assert compile_result.raw_html.replace('\n', '') == (
        '<a class=""href="http://getnikola.com/"title="getnikola.com">getnikola.com</a>'
    )


def test_without_by(do_test):
    compile_result = do_test("""\
        .. link_figure:: http://getnikola.com/
            :title: Nikola | Nikola
            :description: In goes content, out comes a website, ready to deploy.
            :class: link-figure
            :image_url: http://getnikola.com/galleries/demo/tesla2_lg.jpg
            :author: Roberto Alsina
            :author_url: http://ralsina.me/
    """)

    assert compile_result.raw_html.replace('\n', '') == (
        '<div class="link-figure">'
        '<div class="link-figure-media">'
        '<a class="link-figure-image" href="http://getnikola.com/" target="_blank">'
        '<img src="http://getnikola.com/galleries/demo/tesla2_lg.jpg" alt="Nikola | Nikola" />'
        '</a></div><div class="link-figure-content">'
        '<a class="link-figure-title" href="http://getnikola.com/" target="_blank">Nikola | Nikola</a>'
        '<p class="link-figure-description">In goes content, out comes a website, ready to deploy.</p>'
        '<p class="link-figure-author"><a href="http://ralsina.me/" target="_blank">Roberto Alsina</a>'
        '</p></div></div>'
    )


def test_full(do_test):
    compile_result = do_test("""\
        .. link_figure:: http://getnikola.com/
            :title: Nikola | Nikola
            :description: In goes content, out comes a website, ready to deploy.
            :class: link-figure
            :image_url: http://getnikola.com/galleries/demo/tesla2_lg.jpg
            :author: Roberto Alsina
            :author_url: http://ralsina.me/
            :author_by: by
    """)

    assert compile_result.raw_html.replace('\n', '') == (
        '<div class="link-figure">'
        '<div class="link-figure-media">'
        '<a class="link-figure-image" href="http://getnikola.com/" target="_blank">'
        '<img src="http://getnikola.com/galleries/demo/tesla2_lg.jpg" alt="Nikola | Nikola" />'
        '</a></div><div class="link-figure-content">'
        '<a class="link-figure-title" href="http://getnikola.com/" target="_blank">Nikola | Nikola</a>'
        '<p class="link-figure-description">In goes content, out comes a website, ready to deploy.</p>'
        '<p class="link-figure-author">by <a href="http://ralsina.me/" target="_blank">Roberto Alsina</a>'
        '</p></div></div>'
    )


@fixture
def do_test(basic_compile_test):
    def f(data: str) -> CompileResult:
        return basic_compile_test('.rst', data, extra_plugins_dirs=[V7_PLUGIN_PATH / 'link_figure'])

    return f
