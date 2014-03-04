# -*- coding: utf-8 -*-

# Copyright © 2014 Roberto Alsina

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

from __future__ import print_function, unicode_literals
import json
import os

import bottle as b
import mako

from nikola.plugin_categories import Command
from nikola.utils import LOGGER

site = None

class Webapp(Command):

    name = "webapp"
    doc_usage = "[[-u] theme_name] | [[-u] -l]"
    doc_purpose = "install theme into current site"
    cmd_options = []

    def _execute(self, options, args):
        global site
        self.site.scan_posts()
        site = self.site
        b.run(host='localhost', port=8080)

    @staticmethod
    @b.route('/')
    def index():
        context = {}
        context['site'] = site
        return render('index.tpl', context)

    @staticmethod
    @b.route('/edit/<path:path>')
    def index(path):
        context = {'path': path}
        context['site'] = site
        context['json'] = json
        post = None
        for p in site.posts:
            if p.source_path == path:
                post = p
                break
        if post is None:
            b.abort(404, "No such post")
        context['post'] = post
        return render('edit_post.tpl', context)

    @staticmethod
    @b.route('/save/<path:path>', method='POST')
    def save(path):
        context = {'path': path}
        context['site'] = site
        post = None
        for p in site.posts:
            if p.source_path == path:
                post = p
                break
        if post is None:
            b.abort(404, "No such post")
        post.compiler.create_post(post.source_path, onefile=True, is_page=False, **b.request.forms)

    @staticmethod
    @b.route('/static/<path:path>')
    def server_static(path):
        return b.static_file(path, root=os.path.join(os.path.dirname(__file__), 'static'))

lookup = mako.lookup.TemplateLookup(
    directories=os.path.join(os.path.dirname(__file__), 'templates'),
    output_encoding='utf-8')

def render(template_name, context=None):
    if context is None:
        context = {}
    return lookup.get_template(template_name).render_unicode(**context)
