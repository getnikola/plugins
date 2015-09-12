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
from collections import OrderedDict

from docutils import nodes
from docutils.parsers.rst import Directive, directives

from nikola.plugin_categories import RestExtension

from nikola.plugin_categories import LateTask
from nikola.utils import copy_tree


def flag_to_boolean(value):
    """Function to parse directives.flag options"""
    return 'true'


class Plugin(RestExtension, LateTask):

    name = "nanogallery_directive"

    def set_site(self, site):
        self.site = site
        site.template_hooks['extra_head'].append('<link href="/assets/css/nanogallery.min.css" rel="stylesheet" type="text/css">')
        site.template_hooks['body_end'].append('<script type="text/javascript" src="/assets/js/jquery.nanogallery.min.js"></script>')
        NanoGallery.site = site
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


class NanoGallery(Directive):
    """ Restructured text extension for inserting nanogallery galleries."""

    # http://nanogallery.brisbois.fr/#docGeneralSettings
    option_spec = {
        'theme': directives.unchanged,
        'colorscheme': directives.unchanged,
        'rtl': flag_to_boolean,
        'maxitemsperline': directives.nonnegative_int,
        'maxwidth': directives.nonnegative_int,
        'paginationdots': flag_to_boolean,
        'paginationmaxlinesperpage': directives.nonnegative_int,
        'paginationswipe': flag_to_boolean,
        'locationhash': flag_to_boolean,
        'itemsselectable': flag_to_boolean,
        'showcheckboxes': flag_to_boolean,
        'checkboxstyle': directives.unchanged,
        'keepselection': flag_to_boolean,
        'i18n': directives.unchanged,
        'lazybuild': directives.unchanged,
        'lazybuildtreshold': directives.nonnegative_int,
        'openonstart': directives.unchanged,
        'breakpointsizesm': directives.nonnegative_int,
        'breakpointsizeme': directives.nonnegative_int,
        'breakpointsizela': directives.nonnegative_int,
        'breakpointsizexl': directives.nonnegative_int,
        'thumbnailheight': directives.nonnegative_int,
        'thumbnailwidth': directives.nonnegative_int,
        'thumbnailalignment': directives.unchanged,
        'thumbnailgutterwidth': directives.nonnegative_int,
        'thumbnailgutterheight': directives.nonnegative_int,
        'thumbnailopenimage': flag_to_boolean,
        'thumbnaillabel': directives.unchanged,
        'thumbnailhovereffect': directives.unchanged,
        'touchanimation': flag_to_boolean,
        'touchautoopendelay': directives.nonnegative_int,
        'thumbnaildisplayinterval': directives.nonnegative_int,
        'thumbnaildisplaytransition': flag_to_boolean,
        'thumbnaillazyload': flag_to_boolean,
        'thumbnaillazyloadtreshold': directives.nonnegative_int,
        'thumbnailadjustlastrowheight': flag_to_boolean,
        'thumbnailalbumdisplayimage': flag_to_boolean,
    }
    has_content = True

    def __init__(self, *args, **kwargs):
        super(NanoGallery, self).__init__(*args, **kwargs)
        self.state.document.settings.record_dependencies.add('####MAGIC####CONFIG:NANOGALLERY_OPTIONS')

    def _sanitize_options(self):
        THUMBNAIL_SIZE = self.site.config.get('THUMBNAIL_SIZE', 128)
        defaults = {
            'theme': 'clean',
            'maxitemsperline': 4,
            'thumbnailgutterwidth': 10,
            'thumbnailgutterheight': 10,
            'locationhash': 'false',
            'colorscheme': 'lightBackground',
            'thumbnailheight': 'auto',
            'thumbnailwidth': 250,
            'thumbnailhovereffect': 'imageScale150',
            'thumbnaillabel': {'display': 'false'},
        }
        user_defaults = self.site.config.get('NANOGALLERY_OPTIONS', {})
        # from doit.tools import set_trace
        # set_trace()
        defaults.update(user_defaults)

        defaults.update(self.options)
        # TODO: validate options here and (maybe) display an error
        for option in defaults.keys():
            assert option in self.option_spec

        # We need to convert all the lowercase options (rst make them
        # lowercase automatically) to the correct ones -supported by
        # nanoGALLERY Javascript function
        js_options = OrderedDict([
            ('theme', 'theme'),
            ('colorscheme', 'colorScheme'),
            ('rtl', 'RTL'),
            ('maxitemsperline', 'maxItemsPerLine'),
            ('maxwidth', 'maxWidth'),
            ('paginationdots', 'paginationDots'),
            ('paginationmaxlinesperpage', 'paginationMaxLinesPerPage'),
            ('paginationswipe', 'paginationSwipe'),
            ('locationhash', 'locationHash'),
            ('itemsselectable', 'itemsSelectable'),
            ('showcheckboxes', 'showCheckboxes'),
            ('checkboxstyle', 'checkboxStyle'),
            ('keepselection', 'keepSelection'),
            ('i18n', 'i18n'),
            ('lazybuild', 'lazyBuild'),
            ('lazybuildtreshold', 'lazyBuildTreshold'),
            ('openonstart', 'openOnStart'),
            ('breakpointsizesm', 'breakpointSizeSM'),
            ('breakpointsizeme', 'breakpointSizeME'),
            ('breakpointsizela', 'breakpointSizeLA'),
            ('breakpointsizexl', 'breakpointSizeXL'),
            ('thumbnailheight', 'thumbnailHeight'),
            ('thumbnailwidth', 'thumbnailWidth'),
            ('thumbnailalignment', 'thumbnailAlignment'),
            ('thumbnailgutterwidth', 'thumbnailGutterWidth'),
            ('thumbnailgutterheight', 'thumbnailGutterHeight'),
            ('thumbnailopenimage', 'thumbnailOpenImage'),
            ('thumbnaillabel', 'thumbnailLabel'),
            ('thumbnailhovereffect', 'thumbnailHoverEffect'),
            ('touchanimation', 'touchAnimation'),
            ('touchautoopendelay', 'touchAutoOpenDelay'),
            ('thumbnaildisplayinterval', 'thumbnailDisplayInterval'),
            ('thumbnaildisplaytransition', 'thumbnailDisplayTransition'),
            ('thumbnaillazyload', 'thumbnailLazyLoad'),
            ('thumbnaillazyloadtreshold', 'thumbnailLazyLoadTreshold'),
            ('thumbnailadjustlastrowheight', 'thumbnailAdjustLastRowHeight'),
            ('thumbnailalbumdisplayimage', 'thumbnailAlbumDisplayImage')
        ])

        options = {}
        for k in defaults:
            options[js_options[k]] = defaults[k]

        return options

    def run(self):
        if len(self.content) == 0:
            return

        image_list = [t for t in self.content]
        thumbs = ['.thumbnail'.join(os.path.splitext(p)) for p in image_list]

        photo_array = []
        for img, thumb in zip(image_list, thumbs):
            photo_array.append({
                'href': img,
                'data': {
                    'ngthumb': thumb,
                },
            })

        output = self.site.template_system.render_template(
            'embedded-nanogallery.tmpl',
            None,
            {
                'nanogallery_content': photo_array,
                'options': self._sanitize_options()
            }
        )
        return [nodes.raw('', output, format='html')]


directives.register_directive('nanogallery', NanoGallery)
