from io import StringIO
from pathlib import Path

from lxml import html

__all__ = [
    'CompileResult',
    'TEST_DATA_PATH',
    'V7_PLUGIN_PATH',
]

TEST_DATA_PATH = Path(__file__).parent / 'data'

V7_PLUGIN_PATH = Path(__file__).parent.parent / 'v7'


class CompileResult:
    def __init__(self, path: Path):
        dep_file = path.with_suffix(path.suffix + '.dep')
        self.deps = set(dep_file.read_text(encoding='utf8').split()) if dep_file.exists() else set()
        self.raw_html = path.read_text(encoding='utf8')
        self._html_doc = None

    @property
    def html_doc(self):
        if not self._html_doc:
            self._html_doc = html.parse(StringIO(self.raw_html))
        return self._html_doc

    def assert_contains(self, element: str, attributes=None, text=None):
        try:
            tag = next(self.html_doc.iter(element))
        except StopIteration:
            raise Exception("<{0}> not in {1}".format(element, self.raw_html))

        if attributes:
            arg_attrs = set(attributes.items())
            tag_attrs = set(tag.items())
            assert arg_attrs.issubset(tag_attrs)
        if text:
            assert text in tag.text
