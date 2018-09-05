# -*- coding: utf-8 -*-

# Copyright © 2012-2013 Roberto Alsina and others.

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

import json
import os

import lxml

from nikola.plugin_categories import ShortcodePlugin
from nikola.utils import LocaleBorg


class Plugin(ShortcodePlugin):

    name = "gallery_shortcode"

    def set_site(self, site):
        self.site = site
        self.inject_dependency('render_posts', 'render_galleries')
        site.register_shortcode("gallery", self.handler)
        return super().set_site(site)

    def handler(self, gallery_name, *args, **kwargs):
        kw = {
            'output_folder': self.site.config['OUTPUT_FOLDER'],
            'thumbnail_size': self.site.config['THUMBNAIL_SIZE'],
        }
        gallery_index_file = os.path.join(kw['output_folder'], self.site.path('gallery', gallery_name))
        gallery_index_path = self.site.path('gallery', gallery_name)
        gallery_folder = os.path.dirname(gallery_index_path)
        deps = [gallery_index_file]
        with open(gallery_index_file, 'r') as inf:
            data = inf.read()
        dom = lxml.html.fromstring(data)
        text = [e.text for e in dom.xpath('//script') if e.text and 'jsonContent = ' in e.text][0]
        photo_array = json.loads(text.split(' = ', 1)[1].split(';', 1)[0])
        for img in photo_array:
            img['url'] = '/' + '/'.join([gallery_folder, img['url']])
            img['url_thumb'] = '/' + '/'.join([gallery_folder, img['url_thumb']])
        photo_array_json = json.dumps(photo_array)
        context = {}
        context['description'] = ''
        context['title'] = ''
        context['lang'] = LocaleBorg().current_lang
        context['crumbs'] = []
        context['folders'] = []
        context['photo_array'] = photo_array
        context['photo_array_json'] = photo_array_json
        context['permalink'] = '#'
        context.update(self.site.GLOBAL_CONTEXT)
        context.update(kw)
        output = self.site.template_system.render_template(
            'gallery_shortcode.tmpl',
            None,
            context
        )
        return output, deps
