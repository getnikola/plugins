from nikola.plugin_categories import Task
from nikola import utils

import copy
import os
import os.path


class CreateErrorPages(Task):
    name = "create_error_pages"

    def set_site(self, site):
        super(CreateErrorPages, self).set_site(site)

    def prepare_error_page(self, destination, lang, template):
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

        for error in self.site.config.get('CREATE_ERROR_PAGES', []):
            for lang in self.site.config['TRANSLATIONS'].keys():
                destination = os.path.join(self.site.config['OUTPUT_FOLDER'], self.site.config['TRANSLATIONS'][lang], '{}.html'.format(error))
                yield self.prepare_error_page(destination, lang, '{}.tmpl'.format(error))
