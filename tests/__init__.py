from pathlib import Path

from doit.loader import generate_tasks
from doit.task import Stream

from nikola.plugin_categories import Task

__all__ = [
    "execute_plugin_tasks",
    'TEST_DATA_PATH',
    'V7_PLUGIN_PATH',
]

TEST_DATA_PATH = Path(__file__).parent / 'data'

V7_PLUGIN_PATH = Path(__file__).parent.parent / 'v7'


def execute_plugin_tasks(plugin: Task, verbosity: int = 0):
    tasks = generate_tasks(plugin.name, plugin.gen_tasks())
    stream = Stream(verbosity)
    for t in tasks:
        catched = t.execute(stream)
        if catched:
            raise Exception("Task error for '{}'\n{}".format(t.name, catched.get_msg()))
