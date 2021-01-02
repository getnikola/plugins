import os
from textwrap import dedent
from typing import Dict

from tests import execute_plugin_tasks
from v8.plantuml.plantuml import PlantUmlTask


# Note this test is also sufficient to prove that rendering binary image files will work
def test_render_file_success(tmp_site_path):
    (tmp_site_path / 'pages' / 'test.puml').write_text(dedent('''\
        @startuml
        title filename="%filename()"
        participant "unicode ✓"
        participant "defined $defined"
        @enduml
    '''), encoding='utf8')

    (tmp_site_path / 'pages' / 'includes').mkdir()
    (tmp_site_path / 'pages' / 'includes' / 'include1.iuml').write_text('participant "included-1"')
    (tmp_site_path / 'pages' / 'includes' / 'include2.iuml').write_text('participant "included-2"')

    plugin = create_plugin({
        'PLANTUML_ARGS': [
            '-chide footbox',
            '-Ipages/includes/include1.iuml',
        ],
        'PLANTUML_FILES': (
            ('pages/*.puml', '', '.txt', [
                '-c!$defined="DEFINED ✓"',
                '-Ipages/includes/include2.iuml',
                '-tutxt',
            ]),
        ),
    })

    execute_plugin_tasks(plugin)

    assert (tmp_site_path / 'output' / 'test.txt').read_text(encoding='utf8').splitlines() == [
        # Using individual quoted lines to preserve trailing spaces
        '                                     filename="test.puml"                                ',
        '                                                                                         ',
        '     ┌──────────┐          ┌──────────┐          ┌─────────┐          ┌─────────────────┐',
        '     │included-1│          │included-2│          │unicode ✓│          │defined DEFINED ✓│',
        '     └────┬─────┘          └────┬─────┘          └────┬────┘          └────────┬────────┘',
        '          │                     │                     │                        │         ',
    ]


def test_render_file_error(tmp_site_path):
    (tmp_site_path / 'pages' / 'test.puml').write_text(dedent('''\
        @startuml
        A -> B
        this line is bad
        @enduml
    '''))

    plugin = create_plugin({
        'PLANTUML_FILES': (
            ('pages/*.puml', '', '.txt', ['-tutxt']),
        ),
        'PLANTUML_CONTINUE_AFTER_FAILURE': True,
    })

    execute_plugin_tasks(plugin)

    assert (tmp_site_path / 'output' / 'test.txt').read_text().splitlines() == [
        # Using individual quoted lines to preserve trailing spaces
        '[From string (line 3) ]',
        '                       ',
        '@startuml              ',
        'A -> B                 ',
        'this line is bad       ',
        '^^^^^                  ',
        ' Syntax Error?         ',
    ]


def test_gen_tasks(tmp_site_path):
    (tmp_site_path / 'pages' / 'b').mkdir(parents=True)
    (tmp_site_path / 'other' / 'diagrams' / 'd').mkdir(parents=True)

    (tmp_site_path / 'pages' / 'aaa.puml').touch()
    (tmp_site_path / 'pages' / 'b' / 'bbb.puml').touch()
    (tmp_site_path / 'other' / 'diagrams' / 'ccc.puml').touch()
    (tmp_site_path / 'other' / 'diagrams' / 'd' / 'ddd.puml').touch()

    plugin = create_plugin({
        'PLANTUML_FILES': (
            ('pages/*.puml', '', '.txt', []),
            ('other/diagrams/*.puml', 'other', '.png', []),
        ),
    })

    tasks = plugin_tasks(plugin)

    assert sorted(task['targets'][0] for task in tasks) == [
        'output/aaa.txt',
        'output/b/bbb.txt',
        'output/other/ccc.png',
        'output/other/d/ddd.png',
    ]


def test_task_depends_on_included_files(tmp_site_path):
    plugin = create_plugin({
        'PLANTUML_ARGS': [
            '-Iincludes/include1.iuml',
            '-Iincludes/include2.iuml',
            '-Iincludes/bar*.iuml',
            '-Iincludes/baz?.iuml',
        ],
        'PLANTUML_FILES': (
            ('pages/*.puml', '', '.svg', ['-Iincludes/include3.iuml']),
        )
    })

    (tmp_site_path / 'pages' / 'foo.puml').touch()

    tasks = plugin_tasks(plugin)

    # for now, bar*.iuml & baz?.iuml deliberately do not affect file_dep
    assert sorted(tasks[0]['file_dep']) == [
        'includes/include1.iuml',
        'includes/include2.iuml',
        'includes/include3.iuml',
        'pages/foo.puml',
    ]


def create_plugin(config: Dict):
    plugin = PlantUmlTask()
    plugin.set_site(FakeSite(config))
    return plugin


class FakeSite:
    debug = True

    def __init__(self, config: Dict):
        self.config = {
            'FILTERS': {},
            'OUTPUT_FOLDER': 'output',
            'PLANTUML_DEBUG': True,
        }
        self.config.update(config)
        if 'PLANTUML_EXEC' in os.environ:
            self.config['PLANTUML_EXEC'] = os.environ['PLANTUML_EXEC'].split()


def plugin_tasks(plugin):
    tasks = list(plugin.gen_tasks())
    assert tasks.pop(0) == plugin.group_task()
    return tasks
