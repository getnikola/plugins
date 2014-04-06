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
import webbrowser

import bottle as b
import mako

from nikola.plugin_categories import Command

_site = None


def init_site():
    _site.scan_posts(really=True)


class Webapp(Command):

    name = "webapp"
    doc_usage = "[[-u] theme_name] | [[-u] -l]"
    doc_purpose = "install theme into current site"
    cmd_options = [
        {
            'name': 'browser',
            'short': 'b',
            'type': bool,
            'help': 'Start a web browser.',
            'default': False,
        },
        {
            'name': 'port',
            'short': 'p',
            'long': 'port',
            'default': 8001,
            'type': int,
            'help': 'Port nummber (default: 8001)',
        },
    ]

    def _execute(self, options, args):
        global _site
        _site = self.site
        init_site()
        port = options and options.get('port')
        if options and options.get('browser'):
            webbrowser.open('http://localhost:{0}'.format(port))
        b.run(host='localhost', port=port)

    @staticmethod
    @b.route('/')
    def index():
        context = {}
        context['site'] = _site
        return render('index.tpl', context)

    @staticmethod
    @b.route('/edit/<path:path>', method='POST')
    @b.route('/edit/<path:path>', method='GET')
    def edit(path):
        context = {'path': path}
        context['site'] = _site
        context['json'] = json
        post = None
        for p in _site.timeline:
            if p.source_path == path:
                post = p
                break
        if post is None:
            b.abort(404, "No such post or page")
        context['post'] = post
        return render('edit_post.tpl', context)

    @staticmethod
    @b.route('/save/<path:path>', method='POST')
    def save(path):
        # FIXME insecure pending defnull/bottle#411
        context = {'path': path}
        context['site'] = _site
        post = None
        for p in _site.timeline:
            if p.source_path == path:
                post = p
                break
        if post is None:
            b.abort(404, "No such post")
        content = b.request.forms.pop('content')
        post.compiler.create_post(post.source_path, content=content, onefile=True, is_page=False, **b.request.forms)
        init_site()
        b.redirect('/edit/' + path)

    @staticmethod
    @b.route('/delete/<path:path>')
    def delete(path):
        context = {'path': path}
        context['site'] = _site
        post = None
        for p in _site.timeline:
            if p.source_path == path:
                post = p
                break
        if post is None:
            b.abort(404, "No such post")
        context['post'] = post
        return render('delete_post.tpl', context)

    @staticmethod
    @b.route('/really_delete/<path:path>')
    def really_delete(path):
        # FIXME insecure pending defnull/bottle#411
        os.unlink(path)
        init_site()
        b.redirect('/')

    @staticmethod
    @b.route('/static/<path:path>')
    def server_static(path):
        return b.static_file(path, root=os.path.join(os.path.dirname(__file__), 'static'))

    @staticmethod
    @b.route('/new/post', method='POST')
    def new_post():
        title = b.request.forms['title']
        # So, let's create a post with that title, lumberjack style
        # FIXME but I am a lumberjack and I don't care.
        os.system("nikola new_post -t '{0}'".format(title))
        # reload post list and go to index
        init_site()
        b.redirect('/')

    @staticmethod
    @b.route('/new/page', method='POST')
    def new_page():
        title = b.request.forms['title']
        # So, let's create a page with that title, lumberjack style
        # FIXME but I am a lumberjack and I don't care.
        os.system("nikola new_page -t '{0}'".format(title))
        # reload post list and go to index
        init_site()
        b.redirect('/')

lookup = mako.lookup.TemplateLookup(
    directories=os.path.join(os.path.dirname(__file__), 'templates'),
    output_encoding='utf-8')


def render(template_name, context=None):
    if context is None:
        context = {}
    return lookup.get_template(template_name).render_unicode(**context)
