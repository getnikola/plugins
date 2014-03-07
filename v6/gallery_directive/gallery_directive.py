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

from docutils import nodes
from docutils.parsers.rst import Directive, directives
import lxml

from nikola.plugin_categories import RestExtension


class Plugin(RestExtension):

    name = "gallery_directive"

    def set_site(self, site):
        self.site = site
        Gallery.site = site
        directives.register_directive('gallery', Gallery)
        return super(Plugin, self).set_site(site)


class Gallery(Directive):
    """ Restructured text extension for inserting an image gallery

        Usage:

            .. gallery:: foo

   """

    has_content = False
    required_arguments = 1
    optional_arguments = 0

    def run(self):
        gallery_name = self.arguments[0]
        kw = {
            'output_folder': self.site.config['OUTPUT_FOLDER'],
            'gallery_path': self.site.config['GALLERY_PATH'],
            'thumbnail_size': self.site.config['THUMBNAIL_SIZE'],
        }
        gallery_folder = os.path.join(kw['output_folder'], kw['gallery_path'], gallery_name)
        gallery_index = os.path.join(gallery_folder, 'index.html')
        self.state.document.settings.record_dependencies.add(gallery_index)
        with open(gallery_index, 'r') as inf:
            data = inf.read()
        dom = lxml.html.fromstring(data)
        text = [e.text for e in dom.xpath('//script') if e.text and 'jsonContent = ' in e.text][0]
        photo_array = json.loads(text.split(' = ', 1)[1].split(';', 1)[0])
        for img in photo_array:
            img['url'] = '/' + '/'.join([kw['gallery_path'], gallery_name, img['url']])
            img['url_thumb'] = '/' + '/'.join([kw['gallery_path'], gallery_name, img['url_thumb']])
        photo_array_json = json.dumps(photo_array)
        context = {}
        context['description'] = ''
        context['title'] = ''
        context['lang'] = self.site.current_lang()
        context['crumbs'] = []
        context['folders'] = []
        context['photo_array'] = photo_array
        context['photo_array_json'] = photo_array_json
        context.update(self.site.GLOBAL_CONTEXT)
        context.update(kw)
        output = self.site.template_system.render_template(
            'gallery.tmpl',
            None,
            context
        )
        # This magical comment makes everything work. Try removing it!
        output = '\n<!-- foo -->\n%s\n\n\n' % output
        return [nodes.raw('', output, format='html')]
