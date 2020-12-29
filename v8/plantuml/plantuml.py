import os
import subprocess
from itertools import chain
from logging import DEBUG
from pathlib import Path
from typing import List, Sequence

from nikola import utils
from nikola.plugin_categories import Task

DEFAULT_PLANTUML_ARGS = []

DEFAULT_PLANTUML_DEBUG = False

DEFAULT_PLANTUML_EXEC = ['plantuml']

DEFAULT_PLANTUML_FILES = (
    ('pages/*.puml', '', '.svg', ['-tsvg']),
)

DEFAULT_PLANTUML_CONTINUE_AFTER_FAILURE = False


# TODO when 3.5 support is dropped
# - Use capture_output arg in subprocess.run()
# - Change typing annotations

class PlantUmlTask(Task):
    """Renders PlantUML files"""

    name = 'plantuml'

    _common_args = ...  # type: List[str]
    _continue_after_failure = ...  # type: bool
    _exec = ...  # type: List[str]
    _render_errors = ...  # type: bool

    def set_site(self, site):
        super().set_site(site)
        self._common_args = site.config.get('PLANTUML_ARGS', DEFAULT_PLANTUML_ARGS)
        self._continue_after_failure = site.config.get('PLANTUML_CONTINUE_AFTER_FAILURE', DEFAULT_PLANTUML_CONTINUE_AFTER_FAILURE)
        self._exec = site.config.get('PLANTUML_EXEC', DEFAULT_PLANTUML_EXEC)
        if site.config.get('PLANTUML_DEBUG', DEFAULT_PLANTUML_DEBUG):
            self.logger.level = DEBUG

    def gen_tasks(self):
        yield self.group_task()

        filters = self.site.config['FILTERS']
        output_folder = self.site.config['OUTPUT_FOLDER']
        plantuml_files = self.site.config.get('PLANTUML_FILES', DEFAULT_PLANTUML_FILES)
        output_path = Path(output_folder)

        # Logic derived from nikola.plugins.misc.scan_posts.ScanPosts.scan()
        for pattern, destination, extension, args in plantuml_files:
            combined_args = self._common_args + args

            kw = {
                'combined_args': combined_args,
                'filters': filters,
                'output_folder': output_folder,
            }

            # TODO figure out exactly what the PlantUML include patterns do and expand them similarly here
            includes = list(set(a[2:] for a in combined_args if a.startswith('-I') and '*' not in a and '?' not in a))

            pattern = Path(pattern)
            root = pattern.parent

            for src in root.rglob(pattern.name):
                dst = output_path / destination / src.relative_to(root).parent / src.with_suffix(extension).name
                dst_str = str(dst)
                task = {
                    'basename': self.name,
                    'name': dst_str,
                    'file_dep': includes + [str(src)],
                    'targets': [dst_str],
                    'actions': [(self.render_file, [src, dst, combined_args + ['-filename', src.name]])],
                    'uptodate': [utils.config_changed(kw, 'plantuml:' + dst_str)],
                    'clean': True,
                }
                yield utils.apply_filters(task, filters)

    # noinspection PyBroadException
    def render_file(self, src: Path, dst: Path, args: Sequence[str]) -> bool:
        def process_arg(arg):
            return arg \
                .replace('%site_path%', os.getcwd()) \
                .encode('utf8')

        command = list(map(process_arg, chain(self._exec, args, ['-pipe', '-stdrpt'])))

        source = src.read_bytes()

        self.logger.debug('render() exec: %s\n%s', command, source)

        result = subprocess.run(command, input=source, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(result.stdout)

        if result.returncode == 0:
            return True

        try:
            details = str(result.stderr, encoding='utf8').rstrip()
        except Exception:
            details = str(result.stderr)

        # Note we never "continue" when stdout is empty because that likely means PlantUML failed to start
        if len(result.stdout) and self._continue_after_failure:
            self.logger.warn("PlantUML error for '%s' (return code %d): %s", src, result.returncode, details)
            return True

        raise Exception("PlantUML error (return code {}): {}".format(result.returncode, details))
