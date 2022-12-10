import os
import subprocess
from itertools import chain
from logging import DEBUG
from pathlib import Path
from typing import Optional, Sequence, Tuple

from nikola import utils
from nikola.log import get_logger
from nikola.plugin_categories import Task

DEFAULT_PLANTUML_ARGS = []

DEFAULT_PLANTUML_DEBUG = False

DEFAULT_PLANTUML_EXEC = ['plantuml']

DEFAULT_PLANTUML_FILES = (
    ('plantuml/*.puml', 'plantuml', '.svg', ['-tsvg']),
)

DEFAULT_PLANTUML_CONTINUE_AFTER_FAILURE = False


# TODO when 3.5 support is dropped
# - Use capture_output arg in subprocess.run()
# - Change typing annotations

class PlantUmlTask(Task):
    """Renders PlantUML files"""

    name = 'plantuml'

    _common_args = ...  # type: List[str]
    plantuml_manager = ...  # Optional[PlantUmlManager]

    def set_site(self, site):
        super().set_site(site)
        self._common_args = list(site.config.get('PLANTUML_ARGS', DEFAULT_PLANTUML_ARGS))
        self.plantuml_manager = PlantUmlManager(site)

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

    def render_file(self, src: Path, dst: Path, args: Sequence[str]) -> bool:
        output, error = self.plantuml_manager.render(src.read_bytes(), args)
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(output)

        if not error:
            return True

        # Note we never "continue" when output is empty because that likely means PlantUML failed to start
        if len(output) and self.plantuml_manager.continue_after_failure:
            self.logger.warning("'%s': %s", src, error)
            return True

        raise Exception(error)


class PlantUmlManager:
    """PlantUmlManager is used by 'plantuml' and 'plantuml_markdown' plugins"""

    def __init__(self, site) -> None:
        self.continue_after_failure = site.config.get('PLANTUML_CONTINUE_AFTER_FAILURE', DEFAULT_PLANTUML_CONTINUE_AFTER_FAILURE)
        self.exec = site.config.get('PLANTUML_EXEC', DEFAULT_PLANTUML_EXEC)
        self.logger = get_logger('plantuml_manager')
        if site.config.get('PLANTUML_DEBUG', DEFAULT_PLANTUML_DEBUG):
            self.logger.level = DEBUG

    def render(self, source: bytes, args: Sequence[str]) -> Tuple[bytes, Optional[str]]:
        """Returns (output, error)"""

        def process_arg(arg):
            return arg \
                .replace('%site_path%', os.getcwd()) \
                .encode('utf8')

        command = list(map(process_arg, chain(self.exec, args, ['-pipe', '-stdrpt'])))

        self.logger.debug('render() exec: %s\n%s', command, source)

        result = subprocess.run(command, input=source, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if result.returncode == 0:
            return result.stdout, None

        try:
            details = str(result.stderr, encoding='utf8').rstrip()
        except Exception:  # noqa
            details = str(result.stderr)

        return result.stdout, "PlantUML error (return code {}): {}".format(result.returncode, details)
