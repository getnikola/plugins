# -*- coding: utf-8 -*-

# Copyright © 2014 Manuel Kaufmann

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
import json

from nikola.plugin_categories import Task
from nikola import utils


class Plugin(Task):

    name = "random_post"

    def gen_tasks(self):
        urls = [post.permalink() for post in self.site.posts]
        kw = {
            'files_folders': self.site.config['FILES_FOLDERS'],
            'output_folder': self.site.config['OUTPUT_FOLDER'],
        }

        output_filename = os.path.join(
            kw['output_folder'],
            'assets/js/posts.json',
        )
        output_index = os.path.join(
            kw['output_folder'],
            'random/index.html'
        )

        # Yield a task for Doit
        yield {
            'basename': 'random_post',
            'targets': (output_filename, output_index),
            'actions': [
                (create_json, (output_filename, urls)),
                (create_index, (output_index, )),
            ],
            'uptodate': [utils.config_changed({1: self.site.timeline})],
        }


def create_json(output, urls):
    utils.makedirs(os.path.dirname(output))
    with open(output, 'w') as fh:
        fh.write(json.dumps(urls))


HTML_CONTENT = '''
<!DOCTYPE html>
<head>
<meta charset="utf-8">
<title>Redirecting...</title>
<meta name="robots" content="noindex">
</head>
<body>

<script src="//ajax.googleapis.com/ajax/libs/jquery/1.11.1/jquery.min.js"></script>
<script type="text/javascript">
function choose(choices) {
    var index = Math.floor(Math.random() * choices.length);
    return choices[index];
}

function random_post() {
    $.getJSON('/assets/js/posts.json', function(data){
        window.location.href = choose(data);
    });
}
random_post();
</script>
</body>
'''


def create_index(output):
    utils.makedirs(os.path.dirname(output))
    with open(output, 'w') as fh:
        fh.write(HTML_CONTENT)
