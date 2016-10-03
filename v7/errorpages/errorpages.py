# -*- coding: utf-8 -*-

# Copyright © 2016 Felix Fontein
#
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

from nikola.plugin_categories import Task
from nikola import utils

import copy
import os
import os.path


class CreateErrorPages(Task):
    name = "errorpages"

    def prepare_error_page(self, destination, lang, http_error_code, template):
        context = {}

        deps = self.site.template_system.template_deps(template)
        deps.extend(utils.get_asset_path(x, self.site.THEMES) for x in ('bundles', 'parent', 'engine'))
        deps = list(filter(None, deps))
        context['lang'] = lang
        deps_dict = copy.copy(context)
        deps_dict['OUTPUT_FOLDER'] = self.site.config['OUTPUT_FOLDER']
        deps_dict['TRANSLATIONS'] = self.site.config['TRANSLATIONS']
        deps_dict['global'] = self.site.GLOBAL_CONTEXT

        for k, v in self.site.GLOBAL_CONTEXT['template_hooks'].items():
            deps_dict['||template_hooks|{0}||'.format(k)] = v._items

        for k in self.site._GLOBAL_CONTEXT_TRANSLATABLE:
            deps_dict[k] = deps_dict['global'][k](lang)

        deps_dict['navigation_links'] = deps_dict['global']['navigation_links'](lang)

        url_type = None
        if self.site.config['URL_TYPE'] == 'rel_path':
            url_type = 'full_path'

        task = {
            'basename': self.name,
            'name': os.path.normpath(destination),
            'file_dep': deps,
            'targets': [destination],
            'actions': [(self.site.render_template, [template, destination, context, url_type])],
            'clean': True,
            'uptodate': [utils.config_changed(deps_dict, 'nikola.plugins.render_error_pages')]
        }

        yield utils.apply_filters(task, self.site.config["FILTERS"])

    def gen_tasks(self):
        yield self.group_task()

        output_pattern = self.site.config.get('HTTP_ERROR_PAGE_OUTPUT_PATTERN', '{code}.html')
        template_pattern = self.site.config.get('HTTP_ERROR_PAGE_TEMPLATE_PATTERN', '{code}.tmpl')

        for error in self.site.config.get('CREATE_HTTP_ERROR_PAGES', []):
            for lang in self.site.config['TRANSLATIONS'].keys():
                destination = os.path.join(self.site.config['OUTPUT_FOLDER'], self.site.config['TRANSLATIONS'][lang], output_pattern.format(code=error, lang=lang))
                yield self.prepare_error_page(destination, lang, error, template_pattern.format(code=error, lang=lang))
