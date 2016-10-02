from nikola.plugin_categories import Task
from nikola import utils
from nikola import nikola

import lxml

import copy
import os
import os.path

_LOGGER = utils.get_logger('create_404_page', utils.STDERR_HANDLER)


class Create404Page(Task):
    name = "create_404_page"

    def set_site(self, site):
        super(Create404Page, self).set_site(site)

    def prepare_404(self, destination, lang, template):
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
            'uptodate': [utils.config_changed(deps_dict, 'nikola.plugins.render_404_page')]
        }

        yield utils.apply_filters(task, self.site.config["FILTERS"])

    def gen_tasks(self):
        yield self.group_task()

        for lang in self.site.config['TRANSLATIONS'].keys():
            destination = os.path.join(self.site.config['OUTPUT_FOLDER'], self.site.config['TRANSLATIONS'][lang], '404.html')
            yield self.prepare_404(destination, lang, '404.tmpl')
