# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import subprocess
from unittest.mock import patch

from pytest import fixture

from . import V8_PLUGIN_PATH


def test_ditaa_url(do_test):
    with patch.object(subprocess, 'run') as runner:
        runner.return_value = subprocess.CompletedProcess([], 0)
        assert do_test("""\
            .. ditaa::
               :cmdline: --scale 1 --no-separation --svg
               :filename: my_diagram.svg
               :class: my-css-class
               :alt: A cool diagram

               /-----------------+
               | My cool diagram |
               +-----------------/
        """) == (
            '<img alt="A cool diagram" class="my-css-class" src="/diagrams/my_diagram.svg" />'
        )
        run_args = runner.call_args[0][0]
        assert run_args[0] == 'ditaa'
        # run_args[1] is a temporary file name
        assert run_args[2:] == [
            "files/diagrams/my_diagram.svg",
            "--overwrite",
            "--encoding",
            "utf8",
            "--scale",
            "1",
            "--no-separation",
            "--svg",
        ]


@fixture
def do_test(basic_compile_test):
    def f(data: str) -> str:
        return basic_compile_test(
            '.rst',
            data,
            extra_plugins_dirs=[V8_PLUGIN_PATH / 'ditaa'],
            extra_config={
                'DITAA_OUTPUT_FOLDER': 'files/diagrams',
                'DITAA_OUTPUT_URL_PATH': '/diagrams',
            },

        ).raw_html.replace('\n', '')

    return f
