# -*- coding: utf-8 -*-

# Copyright © 2018 Roberto Alsina and others.

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

"""Timestamp files with a blockchain-based opentimestamp."""

import hashlib
import os
import subprocess

from nikola.plugin_categories import Task
from nikola import utils


class OpenTimeStamp(Task):
    """Timestamp files with a blockchain-based opentimestamp."""

    name = "opentimestamps"

    def gen_tasks(self):
        """Timestamp files with a blockchain-based opentimestamp."""
        self.site.scan_posts()
        yield self.group_task()

        def is_timestamped(f_name):
            """Compare file's sha256 with the one in the timestamp."""
            ts_file = f_name + ".ots"
            if os.path.exists(ts_file):
                hash = hashlib.sha256()
                with open(f_name, "rb") as inf:
                    hash.update(inf.read())
                file_hash = hash.hexdigest()

                sig_hash = (
                    subprocess.check_output(["ots", "info", ts_file])
                    .splitlines()[0]
                    .split()[-1]
                    .strip()
                    .decode("ascii")
                )
                return file_hash == sig_hash
            return False

        def timestamp_file(f_name):
            """Request timestamp from OTS for a given file."""
            subprocess.check_call(["ots", "stamp", f_name])

        # Will generate a timestamp file for the source files for all posts and pages
        for p in self.site.timeline:
            for lang in self.site.config["TRANSLATIONS"]:
                f_name = p.translated_source_path(lang)
                if not is_timestamped(f_name):
                    out_name = f_name + ".ots"
                    task = {
                        "basename": str(self.name),
                        "file_dep": [f_name],
                        "name": out_name,
                        "targets": [out_name],
                        "clean": True,
                        "uptodate": [False],
                        "actions": [(utils.remove_file, [out_name]), (timestamp_file, [f_name])],
                    }
                    yield task
