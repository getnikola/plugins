# -*- coding: utf-8 -*-

# Copyright © 2012-2020 Roberto Alsina, Chris Warrick and others.

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

"""Create a new microblog post."""


from datetime import datetime

from nikola.plugins.command.new_post import CommandNewPost


class CommandMicro(CommandNewPost):
    """Create a new microblog post."""

    name = "micro"
    doc_usage = "[options] [path]"
    doc_purpose = "Create a new microblog post"

    def _execute(self, options, args):
        """Create a new microblog post."""
        options['title'] = datetime.now().time().strftime('%H%M%S')
        options['type'] = 'micro'
        options['tags'] = ''
        options['schedule'] = False
        options['is_page'] = False
        options['date-path'] = False
        p = self.site.plugin_manager.getPluginByName('new_post', 'Command').plugin_object
        return p.execute(options, args)
