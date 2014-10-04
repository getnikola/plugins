# -*- coding: utf-8 -*-

# Copyright © 2014 Chris “Kwpolska” Warrick and others.

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

from nikola.plugin_categories import Task
from nikola import utils


class ProjectPages(Task):
    """Render project indexes."""

    name = 'projectpages'
    dates = {}

    def set_site(self, site):
        site.register_path_handler('project', self.project_path)
        return super(ProjectPages, self).set_site(site)

    def project_path(self, name, lang):
        return [_f for _f in self.projects[name].permalink(lang).split('/') if _f]


    def is_project(self, p):
        """Test projecthood of a page."""
        return p.destination_path().startswith(self.site.config['PROJECT_PATH'])

    def find_projects(self):
        """Find all projects."""
        self._projects = [p for p in self.site.timeline if self.is_project(p)]

    @property
    def projects(self):
        """Look for projects if we haven’t already."""
        try:
            return self._projects
        except AttributeError:
            self.find_projects()
            return self._projects

    def gen_tasks(self):
        """Render project list."""

        self.image_ext_list = ['.jpg', '.png', '.jpeg', '.gif', '.svg', '.bmp', '.tiff']
        self.image_ext_list.extend(self.site.config.get('EXTRA_IMAGE_EXTENSIONS', []))

        self.kw = {
            'project_path': self.site.config['PROJECT_PATH'],
            'project_inputs': self.site.config['PROJECT_INPUTS'],
            'output_folder': self.site.config['OUTPUT_FOLDER'],
            'cache_folder': self.site.config['CACHE_FOLDER'],
            'default_lang': self.site.config['DEFAULT_LANG'],
            'filters': self.site.config['FILTERS'],
            'translations': self.site.config['TRANSLATIONS'],
            'global_context': self.site.GLOBAL_CONTEXT,
            'tzinfo': self.site.tzinfo,
        }

        for k, v in self.site.GLOBAL_CONTEXT['template_hooks'].items():
            self.kw['||template_hooks|{0}||'.format(k)] = v._items

        yield self.group_task()

        template_name = "projects.tmpl"

        self.find_projects()

        # Create index.html for each language
        for lang in self.kw['translations']:
            # save navigation links as dependencies
            self.kw['navigation_links|{0}'.format(lang)] = self.kw['global_context']['navigation_links'](lang)

            dst = os.path.join(self.kw['output_folder'], self.kw['translations'][lang], self.kw['project_path'], 'index.html')
            dst = os.path.normpath(dst)

            context = {}
            context["lang"] = lang

            # TODO: tranlsations?
            context["title"] = "Projects"
            context["description"] = None

            context["featured"] = [p for p in self.projects if p.meta('featured')]
            context["projects"] = [p for p in self.projects if not p.meta('hidden')]

            all_meta = [(p.title(), p.meta('status')) for p in self.projects]
            all_meta += [p.meta('previewimage') for p in context["featured"]]

            file_dep = self.site.template_system.template_deps(
                template_name)

            for p in self.projects:
                file_dep += [p.translated_base_path(l) for l in self.kw['translations']]

            yield utils.apply_filters({
                'basename': self.name,
                'name': dst,
                'file_dep': file_dep,
                'targets': [dst],
                'actions': [
                    (self.site.render_template, (template_name, dst, context))],
                'clean': True,
                'uptodate': [utils.config_changed({
                    1: self.kw,
                    2: context,
                    3: self.projects,
                    4: all_meta,
                })],
            }, self.kw['filters'])
