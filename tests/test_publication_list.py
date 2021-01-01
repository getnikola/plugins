# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import re
import sys
from shutil import copytree

import pytest
from pytest import fixture

from tests import CompileResult, TEST_DATA_PATH, V7_PLUGIN_PATH


@pytest.mark.skipif(sys.version_info < (3, 6), reason="Plugin dependency requires 3.6+")
def test_default(do_test, tmp_site_path):
    copytree(TEST_DATA_PATH / 'publication_list', tmp_site_path / 'publication_list')

    expected = (
        '<div class="publication-list">'
        '<h3>2015</h3><ul>'
        '<li class="publication".*>.*One article in 2015.*'
        '<a href="https://example.com/papers/a2015.html">details</a>.*'
        '<a href="/pdf/a2015.pdf">full text</a>.*</li>'
        '<li class="publication".*>.*One conference in 2015.*'
        '<a href="https://example.com/papers/p2015.html">details</a>.*'
        '</li>'
        '</ul><h3>2010</h3><ul>'
        '<li class="publication".*>.*One Book in 2010.*'
        '<a href="https://example.com/papers/b2010.html">details</a>.*'
        '<a href="http://example.org/b2010.pdf">full text</a>.*</li>'
        '</ul></div>'
    )

    compile_result = do_test('''\
        .. publication_list:: publication_list/test.bib publication_list/test1.bib
            :highlight_author: Nikola Tesla
    ''')

    assert compile_result.deps == {
        'publication_list/test.bib',
        'publication_list/test1.bib',
    }

    assert re.search(expected, compile_result.raw_html.replace('\n', ''))


@fixture
def do_test(basic_compile_test):
    def f(data: str) -> CompileResult:
        return basic_compile_test('.rst', data, extra_plugins_dirs=[V7_PLUGIN_PATH / 'publication_list'])

    return f
