import json
import os
import subprocess
from itertools import chain
from logging import DEBUG
from pathlib import Path
from queue import Empty, Queue
from subprocess import Popen
from threading import Lock, Thread, main_thread
from typing import Iterable, List, Optional, Sequence, Tuple

import blinker
import requests
from requests import HTTPError

from nikola import utils
from nikola.log import get_logger
from nikola.plugin_categories import Task

DEFAULT_PLANTUML_FILE_OPTIONS = []

DEFAULT_PLANTUML_DEBUG = False

DEFAULT_PLANTUML_EXEC = ['plantuml']

DEFAULT_PLANTUML_FILES = (
    ('plantuml/*.puml', 'plantuml', '.svg', ['-tsvg']),
)

DEFAULT_PLANTUML_CONTINUE_AFTER_FAILURE = False

DEFAULT_PLANTUML_PICOWEB_RENDER_TIMEOUT_SECONDS = 30

DEFAULT_PLANTUML_PICOWEB_START_COMMAND = ['plantuml', '-picoweb:0:localhost']

DEFAULT_PLANTUML_PICOWEB_START_TIMEOUT_SECONDS = 30

DEFAULT_PLANTUML_PICOWEB_URL = 'http://localhost:%port%'

DEFAULT_PLANTUML_SYSTEM = 'exec'

PICOWEB_URL_ENV_VAR = 'PLANTUML_PICOWEB_URL'


# TODO when 3.5 support is dropped
# - Use capture_output arg in subprocess.run()
# - Change typing annotations

class PlantUmlTask(Task):
    """Renders PlantUML files"""

    name = 'plantuml'

    _file_options = ...  # type: List[str]
    plantuml_manager = ...  # type: Optional[PlantUmlManager]

    def set_site(self, site):
        super().set_site(site)
        if 'PLANTUML_ARGS' in site.config:
            raise Exception('PLANTUML_ARGS is no longer supported, please use PLANTUML_FILE_OPTIONS instead')
        self._file_options = list(site.config.get('PLANTUML_FILE_OPTIONS', DEFAULT_PLANTUML_FILE_OPTIONS))
        self.plantuml_manager = PlantUmlManager.create(site)

    def gen_tasks(self):
        yield self.group_task()

        filters = self.site.config['FILTERS']
        output_folder = self.site.config['OUTPUT_FOLDER']
        plantuml_files = self.site.config.get('PLANTUML_FILES', DEFAULT_PLANTUML_FILES)
        output_path = Path(output_folder)

        # Logic derived from nikola.plugins.misc.scan_posts.ScanPosts.scan()
        for pattern, destination, extension, options in plantuml_files:
            combined_options = self._file_options + options

            kw = {
                'combined_options': combined_options,
                'filters': filters,
                'output_folder': output_folder,
            }

            # TODO figure out exactly what the PlantUML include patterns do and expand them similarly here
            includes = list(set(a[2:] for a in combined_options if a.startswith('-I') and '*' not in a and '?' not in a))

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
                    'actions': [(self.render_file, [src, dst, combined_options + ['-filename', src.name]])],
                    'uptodate': [utils.config_changed(kw, 'plantuml:' + dst_str)],
                    'clean': True,
                }
                yield utils.apply_filters(task, filters)

    def render_file(self, src: Path, dst: Path, options: Sequence[str]) -> bool:
        output, error = self.plantuml_manager.render(src.read_bytes(), options)
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

    @classmethod
    def create(cls, site):
        system = site.config.get('PLANTUML_SYSTEM', DEFAULT_PLANTUML_SYSTEM)
        if system == 'exec':
            return ExecPlantUmlManager(site)
        elif system == 'picoweb':
            return PicowebPlantUmlManager(site)
        else:
            raise ValueError('Unknown PLANTUML_SYSTEM "{}"'.format(system))

    def __init__(self, site) -> None:
        self.continue_after_failure = site.config.get('PLANTUML_CONTINUE_AFTER_FAILURE', DEFAULT_PLANTUML_CONTINUE_AFTER_FAILURE)
        self._logger = get_logger(self.__class__.__name__)
        if site.config.get('PLANTUML_DEBUG', DEFAULT_PLANTUML_DEBUG):
            self._logger.level = DEBUG

    def render(self, source: bytes, options: Sequence[str]) -> Tuple[bytes, Optional[str]]:
        """Returns (output, error)"""
        raise NotImplementedError

    @staticmethod
    def _process_options(options: Iterable[str]) -> Sequence[str]:
        return [o.replace('%site_path%', os.getcwd()) for o in options]


class ExecPlantUmlManager(PlantUmlManager):
    def __init__(self, site) -> None:
        super().__init__(site)
        self._exec = site.config.get('PLANTUML_EXEC', DEFAULT_PLANTUML_EXEC)

    def render(self, source: bytes, options: Sequence[str]) -> Tuple[bytes, Optional[str]]:
        command = [o.encode('utf8') for o in self._process_options(chain(self._exec, options, ['-pipe', '-stdrpt']))]

        self._logger.debug('render() exec: %s\n%s', command, source)

        result = subprocess.run(command, input=source, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if result.returncode == 0:
            return result.stdout, None

        try:
            details = str(result.stderr, encoding='utf8').rstrip()
        except Exception:  # noqa
            details = str(result.stderr)

        return result.stdout, "PlantUML error (return code {}): {}".format(result.returncode, details)


class PicowebPlantUmlManager(PlantUmlManager):
    def __init__(self, site) -> None:
        super().__init__(site)
        self._site = site
        self._lock = Lock()
        self._render_timeout = site.config.get('PLANTUML_PICOWEB_RENDER_TIMEOUT_SECONDS', DEFAULT_PLANTUML_PICOWEB_RENDER_TIMEOUT_SECONDS)
        self._start_command = site.config.get('PLANTUML_PICOWEB_START_COMMAND', DEFAULT_PLANTUML_PICOWEB_START_COMMAND)
        self._start_timeout = site.config.get('PLANTUML_PICOWEB_START_TIMEOUT_SECONDS', DEFAULT_PLANTUML_PICOWEB_START_TIMEOUT_SECONDS)

        if PICOWEB_URL_ENV_VAR in os.environ:
            self._server_available = True
            self._url = os.getenv(PICOWEB_URL_ENV_VAR)
        else:
            # If there is no start command then we assume a server is already running
            self._server_available = self._start_command == []
            self._url = site.config.get('PLANTUML_PICOWEB_URL', DEFAULT_PLANTUML_PICOWEB_URL)

        if self._server_available:
            self._logger.debug('Will use an already running PlantUML PicoWeb server at "%s"', self._url)

        blinker.signal('auto_command_starting').connect(self._on_auto_command_starting)

    def render(self, source: bytes, options: Sequence[str]) -> Tuple[bytes, Optional[str]]:
        self._maybe_start_picoweb()

        data = json.dumps({
            'options': self._process_options(options),
            'source': str(source, 'utf8')
        })

        self._logger.debug('render() %s', data)
        response = requests.post(self._url + '/render', data=data, timeout=self._render_timeout, allow_redirects=False)

        if response.status_code == 200:
            return response.content, self._error_message_from_picoweb_response(response)

        if response.status_code == 302 \
                and response.headers['location'] == '/plantuml/png/oqbDJyrBuGh8ISmh2VNrKGZ8JCuFJqqAJYqgIotY0aefG5G00000':
            raise Exception('This version of PlantUML does not support "POST /render", you need a version >= 1.2021.2')

        try:
            response.raise_for_status()
        except HTTPError as e:
            text = response.text
            if text:
                raise HTTPError("{} - {}".format(e, text), response=e.response)
            else:
                raise

        raise Exception('Unexpected {} response from PlantUML PicoWeb server'.format(response.status_code))

    @staticmethod
    def _error_message_from_picoweb_response(response):
        if 'X-PlantUML-Diagram-Error' in response.headers:
            return "PlantUML Error (line={}): {}".format(
                response.headers['X-PlantUML-Diagram-Error-Line'],
                response.headers['X-PlantUML-Diagram-Error']
            )
        else:
            return None

    def _on_auto_command_starting(self, site):  # noqa
        self._maybe_start_picoweb()

    def _maybe_start_picoweb(self):
        with self._lock:
            if self._server_available:
                return
            PicoWebSupervisor(
                command=self._process_options(self._start_command),
                start_timeout=self._start_timeout,
                url_template=self._url,
                stop_after_main_thread=True,
            )
            self._url = os.environ[PICOWEB_URL_ENV_VAR]
            self._server_available = True


class PicoWebSupervisor:
    def __init__(self, command: Sequence[str], start_timeout, url_template: str, stop_after_main_thread: bool):
        logger = get_logger('plantuml_picoweb')

        command_bytes = [c.encode('utf8') for c in command]
        logger.info('Starting PlantUML Picoweb server, command=%s', command_bytes)

        if stop_after_main_thread:
            # Ensure the logging thread finishes and we dont leave behind an orphan PicoWeb process
            def _stop():
                main_thread().join()
                self.stop()

            Thread(target=_stop, name='plantuml-picoweb-stop').start()

        self._process = Popen(command_bytes, stderr=subprocess.PIPE)

        queue = Queue()

        def process_logging():
            looking_for_port = True
            for line in self._process.stderr:
                if looking_for_port and line.startswith(b'webPort='):
                    queue.put(int(line[8:]))
                    looking_for_port = False
                else:
                    logger.error(str(line, 'utf8').rstrip())

        # Not a daemon thread because those can be stopped abruptly and the final logging lines might be lost
        Thread(target=process_logging, name='plantuml-picoweb-logging').start()

        try:
            port = queue.get(timeout=start_timeout)
        except Empty:
            raise Exception('Timeout waiting for PlantUML PicoWeb server to start')

        url = os.environ[PICOWEB_URL_ENV_VAR] = url_template.replace('%port%', str(port))
        logger.info('PlantUML PicoWeb server is listening at "%s"', url)

    def stop(self):
        if self._process:
            self._process.terminate()
        if PICOWEB_URL_ENV_VAR in os.environ:
            del os.environ[PICOWEB_URL_ENV_VAR]
