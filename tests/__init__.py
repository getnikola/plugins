import re
from functools import lru_cache
from pathlib import Path
from textwrap import dedent

from doit.loader import generate_tasks
from doit.task import Stream

from nikola.plugin_categories import Task

__all__ = [
    'cached_property',
    'execute_plugin_tasks',
    'simple_html_page',
    'TEST_DATA_PATH',
    'V7_PLUGIN_PATH',
    'V8_PLUGIN_PATH',
]

TEST_DATA_PATH = Path(__file__).parent / 'data'
V7_PLUGIN_PATH = Path(__file__).parent.parent / 'v7'
V8_PLUGIN_PATH = Path(__file__).parent.parent / 'v8'


# Python 3.8 has a cached_property() built in
def cached_property(func):
    return property(lru_cache()(func))


def execute_plugin_tasks(plugin: Task, verbosity: int = 0):
    tasks = generate_tasks(plugin.name, plugin.gen_tasks())
    stream = Stream(verbosity)
    for t in tasks:
        catched = t.execute(stream)
        if catched:
            raise Exception("Task error for '{}'\n{}".format(t.name, catched.get_msg()))


def simple_html_page(body: str) -> str:
    return dedent('''
        <!doctype html>
        <html lang="en">
          <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <link href="https://themes.getnikola.com/v8/bootstrap4/demo/assets/css/bootstrap.min.css" rel="stylesheet" type="text/css">
            <link href="https://themes.getnikola.com/v8/bootstrap4/demo/assets/css/baguetteBox.min.css" rel="stylesheet" type="text/css">
            <link href="https://themes.getnikola.com/v8/bootstrap4/demo/assets/css/rst.css" rel="stylesheet" type="text/css">
            <link href="https://themes.getnikola.com/v8/bootstrap4/demo/assets/css/code.css" rel="stylesheet" type="text/css">
            <link href="https://themes.getnikola.com/v8/bootstrap4/demo/assets/css/theme.css" rel="stylesheet" type="text/css">
          </head>
          <body>
            {}
          </body>
        </html>
        ''').format(body)
