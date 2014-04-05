# -*- coding: utf-8 -*-

# Copyright © 2012-2013 Puneeth Chaganti and others.

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

import subprocess
import sys

from blinker import signal

from nikola.plugin_categories import SignalHandler
from nikola.utils import get_logger


class DeployHooks(SignalHandler):
    """ Add custom actions to be performed when new posts are deployed. """

    name = 'deploy_hooks'

    def run_hooks(self, event):
        """ Run the custom hooks that have been attached. """

        if event['clean'] and self.site.config.get('NO_HOOKS_ON_CLEAN', True):
            self.logger.notice("No hooks run, since site was cleaned.")
            return

        for entry_type in ('deployed', 'undeployed'):
            for entry in event[entry_type]:
                hook_key_name = '%s_HOOKS' % entry_type.upper()
                for command in self.site.config.get(hook_key_name, []):

                    if callable(command):
                        command(entry)

                    else:
                        self._run_command(self._format_command(command, entry))

    def set_site(self, site):
        self.site = site
        self.logger = get_logger(self.name, self.site.loghandlers)

        ready = signal('deployed')
        ready.connect(self.run_hooks)

    def _format_command(self, template, entry):
        """ Format a "templatised" command with an entry as the context. """

        context = dict(entry=entry)

        command = self.site.template_system.render_template_to_string(
            template, context
        )

        return command

    def _run_command(self, command):
        """ Run the given command and log errors, if any. """

        self.logger.notice("==> {0}".format(command))
        try:
            subprocess.check_call(command, shell=True)
        except subprocess.CalledProcessError as e:
            self.logger.error('Failed post deploy hook — command {0} '
                              'returned {1}'.format(e.cmd, e.returncode))
            sys.exit(e.returncode)
