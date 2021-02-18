import os
import sys
from pathlib import Path
from textwrap import dedent
from typing import Dict, List, Set

import lxml.html
from _pytest.fixtures import FixtureRequest
from lxml.etree import _Element
from pytest import fixture

from nikola import Nikola
from nikola.post import Post
from nikola.utils import LocaleBorg
from tests import cached_property, getenv_split, simple_html_page


@fixture
def basic_compile_test(request, tmp_site_path):
    def f(ext: str, data: str, extra_plugins_dirs: List[Path] = None, metadata: str = None, extra_config: Dict = None) -> CompileResult:
        data = dedent(data)
        (tmp_site_path / 'pages' / 'test').with_suffix(ext).write_text(data, encoding='utf8')

        metadata = metadata or '.. title: test'
        (tmp_site_path / 'pages' / 'test').with_suffix('.meta').write_text(metadata, encoding='utf8')

        config = {
            'EXTRA_PLUGINS_DIRS': map(str, extra_plugins_dirs or []),
            'PAGES': (
                ('pages/*' + ext, 'pages', 'page.tmpl'),
            ),
        }
        if extra_config:
            config.update(extra_config)

        site = Nikola(**config)
        site.init_plugins()
        site.scan_posts()

        post = site.timeline[0]
        post.compile('en')
        return CompileResult(request, post)

    return f


class CompileResult:
    """
    CompileResult can be used as a Context Manager e.g.

        def test_example(basic_compile_test):
            with basic_compile_test(...) as compiled:
                assert compiled.raw_html == 'foo'

    If the above assertion fails then:
        1. raw_html is printed to stderr.

        2. A file named "<TEST_FILE_NAME>.test_example.failed.html" will be created next to the test file.
           The html BODY will contain raw_html from the failure.  This lets us quickly view the problem in a browser.

    If the test is re-run and all assertions pass then failure file will be deleted.
    """

    def __init__(self, request: FixtureRequest, post: Post):
        self.request = request
        self.post = post

    @cached_property
    def compiled_path(self) -> Path:
        return Path(self.post.translated_base_path('en'))

    @cached_property
    def deps(self) -> Set[str]:
        dep_file = self.compiled_path.with_suffix(self.compiled_path.suffix + '.dep')
        return set(dep_file.read_text(encoding='utf8').split()) if dep_file.exists() else set()

    @cached_property
    def document(self) -> _Element:
        return lxml.html.document_fromstring(self.raw_html)

    @cached_property
    def raw_html(self) -> str:
        return self.compiled_path.read_text(encoding='utf8')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        test_file = Path(self.request.fspath)
        failed_file = test_file.with_name(test_file.stem + '.' + self.request.node.name + '.failed.html')
        if exc_type:
            print('=== raw_html ====', file=sys.stderr)
            print(self.raw_html, file=sys.stderr)
            print('=== end of raw_html ====', file=sys.stderr)
            failed_file.write_text(simple_html_page(self.raw_html), encoding='utf8')
        elif failed_file.exists():
            failed_file.unlink()


@fixture(scope='session')
def default_locale() -> str:
    return os.environ.get('NIKOLA_LOCALE_DEFAULT', 'en')


@fixture(scope='module', autouse=True)
def localeborg_setup(default_locale):
    """
    Reset the LocaleBorg before and after every test.
    """
    LocaleBorg.reset()
    LocaleBorg.initialize({}, default_locale)
    try:
        yield
    finally:
        LocaleBorg.reset()


@fixture
def maybe_plantuml_picoweb_server(tmp_site_path):
    if os.getenv('PLANTUML_SYSTEM') == 'picoweb':
        from v8.plantuml.plantuml import DEFAULT_PLANTUML_PICOWEB_START_COMMAND, DEFAULT_PLANTUML_PICOWEB_START_TIMEOUT_SECONDS, \
            DEFAULT_PLANTUML_PICOWEB_URL, PicoWebSupervisor
        supervisor = PicoWebSupervisor(
            command=getenv_split('PLANTUML_PICOWEB_START_COMMAND', DEFAULT_PLANTUML_PICOWEB_START_COMMAND),
            start_timeout=os.getenv('PLANTUML_PICOWEB_START_TIMEOUT_SECONDS', DEFAULT_PLANTUML_PICOWEB_START_TIMEOUT_SECONDS),
            url_template=os.getenv('PLANTUML_PICOWEB_URL', DEFAULT_PLANTUML_PICOWEB_URL),
            stop_after_main_thread=False,
        )
        yield
        supervisor.stop()
    else:
        yield


@fixture
def tmp_site_path(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    (tmp_path / 'pages').mkdir()
    return tmp_path
