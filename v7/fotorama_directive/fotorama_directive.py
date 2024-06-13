# -*- coding: utf-8 -*-

# Copyright © 2015 Manuel Kaufmann

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

from __future__ import unicode_literals

import os

from docutils import nodes
from docutils.parsers.rst import Directive, directives

from nikola.plugin_categories import RestExtension

from nikola.plugin_categories import LateTask
from nikola.utils import copy_tree


class Plugin(RestExtension, LateTask):

    name = "fotorama_directive"

    def set_site(self, site):
        self.site = site
        site.template_hooks['extra_head'].append('<link href="/assets/css/fotorama.css" rel="stylesheet" type="text/css">')
        site.template_hooks['body_end'].append('<script src="/assets/js/fotorama.js">')
        Fotorama.site = site
        return super(Plugin, self).set_site(site)

    def gen_tasks(self):
        kw = {
            "output_folder": self.site.config['OUTPUT_FOLDER'],
        }

        # Copy all the assets to the right places
        asset_folder = os.path.join(os.path.dirname(__file__), "files")
        for task in copy_tree(asset_folder, kw["output_folder"]):
            task["basename"] = str(self.name)
            yield task


class Fotorama(Directive):
    """ Restructured text extension for inserting fotorama galleries."""

    # http://fotorama.io/customize/options/
    option_spec = {
        'width': directives.unchanged,
        'minwidth': directives.unchanged,
        'maxwidth': directives.unchanged,
        'height': directives.unchanged,
        'minheight': directives.unchanged,
        'maxheight': directives.unchanged,
        'ratio': directives.unchanged,
        'margin': directives.nonnegative_int,
        'glimpse': directives.unchanged,
        'nav': lambda arg: directives.choice(arg, ('dots', 'thumbs', 'false')),
        'navposition': lambda arg: directives.choice(arg, ('bottom', 'top')),
        'navwidth': directives.unchanged,
        'thumbwidth': directives.nonnegative_int,
        'thumbheight': directives.nonnegative_int,
        'thumbmargin': directives.nonnegative_int,
        'thumbborderwidth': directives.nonnegative_int,
        'allowfullscreen': lambda arg: directives.choice(arg, ('false', 'true', 'native')),
        'fit': lambda arg: directives.choice(arg, ('contain', 'cover', 'scaledown', 'none')),
        'thumbfit': directives.unchanged,
        'transition': lambda arg: directives.choice(arg, ('slide', 'crossfade', 'disolve')),
        'clicktransition': directives.unchanged,
        'transitionduration': directives.nonnegative_int,
        'captions': directives.flag,
        'hash': directives.flag,
        'startindex': directives.unchanged,
        'loop': directives.flag,
        'autoplay': directives.unchanged,
        'stopautoplayontouch': directives.unchanged,
        'keyboard': directives.unchanged,
        'arrows': lambda arg: directives.choice(arg, ('true', 'false', 'always')),
        'click': directives.flag,
        'swipe': directives.flag,
        'trackpad': directives.flag,
        'shuffle': directives.flag,
        'direction': lambda arg: directives.choice(arg, ('ltr', 'rtl')),
        'spinner': directives.unchanged,
        'shadows': directives.flag,
    }
    has_content = True

    def __init__(self, *args, **kwargs):
        super(Fotorama, self).__init__(*args, **kwargs)
        # self.state.document.record_depenence(self.site.)
        # from doit.tools import set_trace; set_trace()
        self.state.document.settings.record_dependencies.add(self.site.configuration_filename)

    def _sanitize_options(self):
        THUMBNAIL_SIZE = self.site.config.get('THUMBNAIL_SIZE', 128)
        defaults = {
            'nav': 'thumbs',
            'ratio': '16/9',
            'keyboard': 'true',
            'thumbwidth': THUMBNAIL_SIZE,
            'thumbheight': THUMBNAIL_SIZE,
            'allowfullscreen': 'native'
        }
        user_defaults = self.site.config.get('FOTORAMA_OPTIONS', {})
        # from doit.tools import set_trace
        # set_trace()
        defaults.update(user_defaults)

        # TODO: validate options here and (maybe) display an error
        defaults.update(self.options)
        for option in defaults.keys():
            assert option in self.option_spec

        return defaults

    def run(self):
        if len(self.content) == 0:
            return

        image_list = [t for t in self.content]
        thumbs = ['.thumbnail'.join(os.path.splitext(p)) for p in image_list]

        photo_array = []
        for img, thumb in zip(image_list, thumbs):
            photo_array.append({
                'url': img,
                'url_thumb': thumb,
            })

        output = self.site.template_system.render_template(
            'embedded-fotorama.tmpl',
            None,
            {
                'fotorama_content': photo_array,
                'options': self._sanitize_options()
            }
        )
        return [nodes.raw('', output, format='html')]


directives.register_directive('fotorama', Fotorama)
