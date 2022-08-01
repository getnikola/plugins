import os
import sys

import pytest
from pytest import fixture

if sys.version_info < (3, 6):
    raise pytest.skip("plantuml_markdown plugin requires Python >= 3.6", allow_module_level=True)

from tests import V8_PLUGIN_PATH
from tests.conftest import CompileResult
from v8.plantuml_markdown.plantuml_markdown import PlantUmlMarkdownProcessor, first_line_for_listing_block


def test_svg(do_fence_test):
    with do_fence_test('plantuml') as compiled:
        assert set(compiled.document.xpath('//svg//text/text()')) == {'Alice', 'Bob', 'hello1', 'hello2'}
        assert '<?xml' not in compiled.raw_html


def test_listing(do_fence_test):
    with do_fence_test('{ .plantuml listing }') as compiled:
        assert compiled.document.xpath('//pre/text()') == [(
            'Alice -> Bob : hello1\n'
            'Bob -> Alice : hello2\n'
        )]


def test_id(do_fence_test):
    with do_fence_test('{ .plantuml svg+listing #foo }') as compiled:
        assert compiled.document.xpath('/html/body/div/@id') == ['foo']
        assert compiled.document.xpath('//pre/a/@name') == ['foo-1', 'foo-2']
        assert compiled.raw_html.count('foo') == 7  # ensure the id is not anywhere unexpected


def test_line_numbering(do_fence_test):
    with do_fence_test('{ .plantuml listing #foo linenos=y }') as compiled:
        assert compiled.document.xpath('//table/tr//code/@data-line-number') == ['1', '2']
        assert compiled.document.xpath('//table/tr//a/@href') == ['#foo-1', '#foo-2']


def test_line_highlighting(do_fence_test):
    with do_fence_test('{ .plantuml listing hl_lines="1 2" }') as compiled:
        assert len(compiled.document.xpath('//pre/span[@class="hll"]')) == 2


def test_svg_and_listing(do_fence_test):
    with do_fence_test('{ .plantuml svg+listing }') as compiled:
        assert [e.tag for e in compiled.document.xpath('/html/body/div/div/*')] == ['svg', 'div']


def test_listing_and_svg(do_fence_test):
    with do_fence_test('{ .plantuml listing+svg }') as compiled:
        assert [e.tag for e in compiled.document.xpath('/html/body/div/div/*')] == ['div', 'svg']


def test_prefix(do_compile_test):
    with do_compile_test("""\
            ```plantuml-prefix
            title Title 1
            footer Footer 1
            ```

            ```plantuml
            Participant foo
            ```

            ```plantuml
            Participant bar
            ```

            ```plantuml-prefix
            title Title 2
            ' no footer this time
            ```

            ```plantuml
            Participant baz
            ```
            """) as compiled:
        text = compiled.document.xpath('//svg//text/text()')
        assert text.count('Title 1') == 2
        assert text.count('Footer 1') == 2
        assert text.count('Title 2') == 1


def test_with_other_markdown(do_compile_test):
    with do_compile_test("""\
            # Heading

            ```plantuml
            Participant foo
            ```

            ```python
            # comment
            ```
            """) as compiled:
        assert compiled.document.xpath('//h1/text()') == ['Heading']
        assert compiled.document.xpath('//svg//text/text()') == ['foo']
        assert compiled.document.xpath('//pre//span[@class="c1"]/text()') == ['# comment']


def test_plantuml_syntax_error(do_compile_test):
    with do_compile_test("""\
            ```plantuml
            this line is bad
            ```
            """, plantuml_continue_after_failure=True) as compiled:
        text = compiled.document.xpath('//svg//text/text()')
        assert '[From string (line 2) ]' in text
        assert 'this line is bad' in text
        assert 'Syntax Error?' in text


@pytest.mark.parametrize('line, expected', [
    (
            '```plantuml',
            '```text',
    ),
    (
            '```.plantuml hl_lines="3 4"',
            '```text hl_lines="3 4"',
    ),
    (
            '```{.plantuml}',
            '```{.text}',
    ),
    (
            '```{ .plantuml #bar }',
            '```{ .text anchor_ref=bar }',
    ),
    (
            '```{ .plantuml #bad<>&chars }',
            '```{ .text anchor_ref=badchars }',
    ),
    (
            '```{ .plantuml #bar .foo linenos=y }',
            '```{ .text anchor_ref=bar .foo linenos=y }',
    ),
])
def test_first_line_for_listing_block(line, expected):
    match = PlantUmlMarkdownProcessor.FENCED_BLOCK_RE.search(line + '\n```')
    assert match
    assert first_line_for_listing_block(match) == expected


@fixture
def do_compile_test(basic_compile_test):
    def f(data: str, plantuml_continue_after_failure=False) -> CompileResult:
        return basic_compile_test(
            '.md',
            data,
            extra_config={
                'PLANTUML_DEBUG': True,
                'PLANTUML_CONTINUE_AFTER_FAILURE': plantuml_continue_after_failure,
                'PLANTUML_EXEC': os.environ.get('PLANTUML_EXEC', 'plantuml').split(),
                'PLANTUML_MARKDOWN_ARGS': [
                    '-chide footbox',
                    '-nometadata',
                    '-Sshadowing=false',
                ],
            },
            extra_plugins_dirs=[
                V8_PLUGIN_PATH / 'plantuml',
                V8_PLUGIN_PATH / 'plantuml_markdown',
            ]
        )

    return f


@fixture
def do_fence_test(do_compile_test):
    def f(fence: str) -> CompileResult:
        return do_compile_test("""\
                ```{}
                Alice -> Bob : hello1
                Bob -> Alice : hello2
                ```
            """.format(fence))

    return f
