import os
import re
import sys

import pytest
from pytest import fixture

if sys.version_info < (3, 6):
    raise pytest.skip("plantuml_markdown plugin requires Python >= 3.6", allow_module_level=True)

from tests import V8_PLUGIN_PATH, regex
from tests.conftest import CompileResult
from v8.plantuml_markdown.plantuml_markdown import PlantUmlMarkdownProcessor, first_line_for_listing_block


def test_svg(do_fence_test):
    with do_fence_test('plantuml') as compiled:
        assert compiled.raw_html == regex(
            '<div>'
            '<div class="plantuml" style="display: inline-block; vertical-align: top;">'
            '<svg .*?>'
            '.*<text .*?>Alice</text>'
            '.*<text .*?>Bob</text>'
            '.*<text .*?>hello1</text>'
            '.*<text .*?>hello2</text>'
            '.*</svg>'
            '</div>'
            '</div>'
        )
        assert '<?xml' not in compiled.raw_html


def test_listing(do_fence_test):
    with do_fence_test('{ .plantuml listing }') as compiled:
        assert compiled.raw_html == (
            '<div>'
            '<div class="plantuml" style="display: inline-block; vertical-align: top;">'
            '<pre class="code literal-block">'
            'Alice -&gt; Bob : hello1\n'
            'Bob -&gt; Alice : hello2\n'
            '</pre>'
            '</div>'
            '</div>'
        )


def test_id(do_fence_test):
    with do_fence_test('{ .plantuml svg+listing #foo }') as compiled:
        assert compiled.raw_html == regex(
            '<div id="foo">'
            '.*<pre class="code literal-block">'
            '<a name="foo-1"></a>Alice -&gt; Bob : hello1\n'
            '<a name="foo-2"></a>Bob -&gt; Alice : hello2\n'
            '</pre>'
            '.*</div>',
            re.DOTALL
        )
        assert compiled.raw_html.count('foo') == 3


def test_line_numbering(do_fence_test):
    with do_fence_test('{ .plantuml listing #foo linenos=y }') as compiled:
        assert compiled.raw_html == regex(
            '<div id="foo">'
            '.*<table class="codetable">'
            '.*<a href="#foo-1">.*<code><a name="foo-1"></a>Alice -&gt; Bob : hello1\n</code>'
            '.*<a href="#foo-2">.*<code><a name="foo-2"></a>Bob -&gt; Alice : hello2\n</code>'
            '.*</table>'
            '.*</div>',
            re.DOTALL
        )
        assert compiled.raw_html.count('foo') == 5


def test_line_highlighting(do_fence_test):
    with do_fence_test('{ .plantuml listing hl_lines="1 2" }') as compiled:
        assert compiled.raw_html == regex(
            '<div>'
            '<div class="plantuml" style="display: inline-block; vertical-align: top;">'
            '<pre class="code literal-block">'
            '<span class="hll">Alice -&gt; Bob : hello1\n</span>'
            '<span class="hll">Bob -&gt; Alice : hello2\n</span>'
            '</pre>'
            '</div>'
            '</div>',
            re.DOTALL
        )


def test_svg_and_listing(do_fence_test):
    with do_fence_test('{ .plantuml svg+listing }') as compiled:
        assert compiled.raw_html == regex(
            '<div>'
            '<div class="plantuml" style="display: inline-block; vertical-align: top;">'
            '<svg .*?>.*</svg>'
            '</div>'
            '<div class="plantuml" style="display: inline-block; vertical-align: top;">'
            '<pre class="code literal-block">.*</pre>'
            '</div>'
            '</div>',
            re.DOTALL
        )


def test_listing_and_svg(do_fence_test):
    with do_fence_test('{ .plantuml listing+svg }') as compiled:
        assert compiled.raw_html == regex(
            '<div>'
            '<div class="plantuml" style="display: inline-block; vertical-align: top;">'
            '<pre class="code literal-block">.*</pre>'
            '</div>'
            '<div class="plantuml" style="display: inline-block; vertical-align: top;">'
            '<svg .*?>.*</svg>'
            '</div>'
            '</div>',
            re.DOTALL
        )


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
        assert compiled.raw_html == regex(
            '.*<svg .*?>'
            '.*<text .*?>Title 1</text>'
            '.*<text .*?>foo</text>'
            '.*<text .*?>Footer 1</text>'
            '.*</svg>'
            '.*<svg .*?>'
            '.*<text .*?>Title 1</text>'
            '.*<text .*?>bar</text>'
            '.*<text .*?>Footer 1</text>'
            '.*</svg>'
            '.*<svg .*?>'
            '.*<text .*?>Title 2</text>'
            '.*<text .*?>baz</text>'
            '.*</svg>'
            , re.DOTALL
        )

        assert compiled.raw_html.count('Footer') == 2


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
        assert compiled.raw_html == regex(
            '<h1>Heading</h1>'
            '.*<svg .*?>'
            '.*<text .*?>foo</text>'
            '.*</svg>'
            '.*<pre class="code literal-block"><span class="c1"># comment</span>'
            , re.DOTALL
        )


def test_plantuml_syntax_error(do_compile_test):
    with do_compile_test("""\
            ```plantuml
            this line is bad
            ```
            """, plantuml_continue_after_failure=True) as compiled:
        assert compiled.raw_html == regex(
            '<div>'
            '<div class="plantuml" style="display: inline-block; vertical-align: top;">'
            '<svg .*?>'
            '.*<text .*?>\\[From string \\(line 2\\) \\]</text>'
            '.*<text .*?>this line is bad</text>'
            '.*<text .*?>Syntax Error\\?</text>'
            '.*</svg>'
            '</div>'
            '</div>',
            re.DOTALL
        )


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
