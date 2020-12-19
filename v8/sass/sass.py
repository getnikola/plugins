# -*- coding: utf-8 -*-

# Copyright © 2020 Renat Galin.

# Permission is hereby granted, free of charge, to any
# person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the
# Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the
# Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice
# shall be included in all copies or substantial portions of
# the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
# KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
# PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS
# OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import os
import sass
from pathlib import Path

from nikola.plugin_categories import Task
from nikola import utils


class BuildSass(Task):
    """Generate CSS out of Sass sources."""

    name = "build_sass"

    def gen_tasks(self):
        """Generate CSS out of Sass sources."""
        self.compiler_name = self.site.config['SASS_COMPILER']
        self.output_folder = self.site.config['OUTPUT_FOLDER']
        self.theme = self.site.config['THEME']

        # Build targets and write CSS files
        destination_path = os.path.join(self.output_folder, 'assets', 'css', self.theme + '.css')
        sass_path = os.path.join('themes', self.theme, 'sass')
        target_path = os.path.join(sass_path, 'index.scss')
        sass_dir_size = ''

        def compile_sass(target_path, destination_path):
            try:
                compiled = sass.compile(filename=target_path)
            except OSError:
                utils.req_missing([self.compiler_name],
                                  'build Sass files (and use this theme)',
                                  False, False)

            with open(destination_path, "w+") as outfile:
                outfile.write(compiled)

        if os.path.isfile(target_path):
            sass_dir_size = sum(f.stat().st_size for f in Path(sass_path).glob('**/*') if f.is_file())

            yield {
                'basename': self.name,
                'name': destination_path,
                'targets': [destination_path],
                'actions': ((compile_sass, [target_path, destination_path]),),
                'uptodate': [utils.config_changed(str(sass_dir_size))],
                'clean': True
            }
