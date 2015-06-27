# A WordPress compiler plugin for Nikola
#
# Copyright (C) 2014-2015 by the contributors
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from __future__ import unicode_literals

import os
import inspect
import io
import pickle
import re
import sys

from nikola.plugin_categories import PageCompiler
from nikola.utils import makedirs, write_metadata
from nikola.utils import get_logger, STDERR_HANDLER
from nikola import utils

from yapsy.PluginManager import PluginManager

from pkg_resources import resource_filename

from . import default_filters, shortcodes

_LOGGER = get_logger('compile_wordpress', STDERR_HANDLER)


class Context:
    id = None

    def __init__(self, id):
        self.id = id
        self.__file_deps_fragment = set()
        self.__file_deps_page = set()
        self.__uptodate_deps_fragment = list()
        self.__uptodate_deps_page = list()

    def add_file_dependency(self, filename, add='both'):
        if add not in {'fragment', 'page', 'both'}:
            raise Exception("Add parameter is '{0}', but must be either 'fragment', 'page', or 'both'.".format(add))
        if add == 'fragment' or add == 'both':
            self.__file_deps_fragment.add(filename)
        if add == 'page' or add == 'both':
            self.__file_deps_page.add(filename)

    def add_uptodate_dependency(self, uptodate_dependency, add='both'):
        if add not in {'fragment', 'page', 'both'}:
            raise Exception("Add parameter is '{0}', but must be either 'fragment', 'page', or 'both'.".format(add))
        if add == 'fragment' or add == 'both':
            self.__uptodate_deps_fragment.append(uptodate_dependency)
        if add == 'page' or add == 'both':
            self.__uptodate_deps_page.append(uptodate_dependency)

    def has_dependencies(self):
        return (len(self.__file_deps_fragment) > 0 or len(self.__file_deps_page) > 0 or
                len(self.__uptodate_deps_fragment) > 0 or len(self.__uptodate_deps_page) > 0)

    def get_file_dependencies_fragment(self):
        return sorted(list(self.__file_deps_fragment))

    def get_file_dependencies_page(self):
        return sorted(list(self.__file_deps_page))

    def get_uptodate_dependencies_fragment(self):
        return self.__uptodate_deps_fragment

    def get_uptodate_dependencies_page(self):
        return self.__uptodate_deps_page

    def __str__(self):
        return "Context<" + str(self.id) + ">(" + str(self.__file_deps_fragment) + ", " + str(self.__file_deps_page) + ", " + str(self.__uptodate_deps_fragment) + ", " + str(self.__uptodate_deps_page) + ")"


class CompileWordpress(PageCompiler):
    """Compiles a subset of Wordpress into HTML."""

    name = "latex"
    demote_headers = True
    site = None

    def __init__(self):
        super().__init__()
        self.__filters = dict()
        self.__shortcodes = shortcodes.ShortCodes()
        self.__default_wordpress_filters = default_filters.DefaultWordpressFilters(self.__shortcodes)

        self.add_filter("the_content", lambda data, context: self.__default_wordpress_filters.wptexturize(data))
        self.add_filter("the_content", lambda data, context: self.__default_wordpress_filters.convert_smilies(data))
        self.add_filter("the_content", lambda data, context: self.__default_wordpress_filters.convert_chars(data))
        self.add_filter("the_content", lambda data, context: self.__default_wordpress_filters.wpautop(data))
        self.add_filter("the_content", lambda data, context: self.__default_wordpress_filters.shortcode_unautop(data))
        self.add_filter('the_content', lambda data, context: self.__shortcodes.do_shortcode(data, context), 11)  # AFTER wpautop()

    def _register_plugins(self):
        # Add directory containing the wordpress module to the Module Search Path.
        # This ensures that plugins can simply do
        #      from wordpress import WordPressPlugin
        # to obtain the WordPressPlugin object.
        abs_wordpress_path = os.path.abspath(inspect.getfile(inspect.currentframe()))  # the absolute path to wordpress/wordpress.py
        abs_dir = os.path.dirname(os.path.dirname(abs_wordpress_path))  # the absolute path to the parent of wordpress
        sys.path.append(abs_dir)

        from wordpress import WordPressPlugin

        self._plugin_manager = PluginManager(categories_filter={
            "WordPressPlugin": WordPressPlugin,
        })
        self._plugin_manager.setPluginInfoExtension('wpplugin')

        # create list of places
        encode = (lambda x: x) if sys.version_info[0] == 3 else utils.sys_encode
        places = [os.path.join(os.getcwd(), encode('plugins'))]
        for dir in self.site.config['EXTRA_PLUGINS_DIRS']:
            places.append(dir)
        places.append(resource_filename('nikola', os.path.join(encode('plugins'))))
        self._plugin_manager.setPluginPlaces(places)

        # collect plugins
        self._plugin_manager.collectPlugins()
        for plugin in self._plugin_manager.getPluginsOfCategory("WordPressPlugin"):
            plugin.plugin_object.register(self)

    def register_head_code(self, head_function):
        # FIXME: implement
        # (not even sure if it's really implementable...)
        pass

    def add_filter(self, tag, filter_function, priority=10):
        if tag not in self.__filters:
            self.__filters[tag] = list()
        f = self.__filters[tag]
        # find where to insert priority
        i = 0
        while i < len(f) and f[i][0] < priority:
            i += 1
        if i < len(f) and f[i][0] > priority:
            f.insert(i, (priority, list()))
        elif i == len(f):
            f.append((priority, list()))
        f[i][1].append(filter_function)

    def filter(self, tag, data, context):
        if tag not in self.__filters:
            return data
        for prio, fs in self.__filters[tag]:
            for f in fs:
                data = f(data, context)
        return data

    def register_shortcode(self, tag, function):
        self.__shortcodes.register_shortcode(tag, function)

    def unregister_shortcode(self, tag):
        self.__shortcodes.unregister_shortcode(tag)

    def do_shortcode(self, data):
        return self.__shortcodes.do_shortcode(data)

    def set_site(self, site):
        super().set_site(site)
        self._register_plugins()

    def __formatData(self, data, context, source=None):
        output = self.filter("the_content", data, context)
        left_shortcodes = self.__shortcodes.get_containing_shortcodes_set(output)
        if len(left_shortcodes) > 0 and source is not None:
            _LOGGER.warning("The post '" + source + "' still contains shortcodes: " + str(left_shortcodes))
        return output

    def compile_to_string(self, source_data):
        context = Context(hash(source_data))
        return self.__formatData(source_data, context)

    def _read_extra_deps(self, post):
        dep_path = post.base_path + '.dep'
        if os.path.isfile(dep_path):
            with io.open(dep_path, 'rb') as file:
                result = pickle.load(file)
                if type(result) == tuple and len(result) == 4:
                    return result
        return ([], [], [], [])

    def register_extra_dependencies(self, post):
        post.add_dependency(lambda: self._read_extra_deps(post)[0], 'fragment')
        post.add_dependency(lambda: self._read_extra_deps(post)[1], 'page')
        post.add_dependency_uptodate(lambda: self._read_extra_deps(post)[2], True, 'fragment')
        post.add_dependency_uptodate(lambda: self._read_extra_deps(post)[3], True, 'page')

    def _write_deps(self, context, dest):
        deps_path = dest + '.dep'
        if context.has_dependencies():
            data = (context.get_file_dependencies_fragment(), context.get_file_dependencies_page(),
                    context.get_uptodate_dependencies_fragment(), context.get_uptodate_dependencies_page())
            with io.open(deps_path, "wb") as file:
                pickle.dump(data, file, pickle.HIGHEST_PROTOCOL)
        else:
            if os.path.isfile(deps_path):
                os.unlink(deps_path)

    def compile_html(self, source, dest, is_two_file=False):
        makedirs(os.path.dirname(dest))
        with io.open(dest, "w+", encoding="utf8") as out_file:
            with io.open(source, "r", encoding="utf8") as in_file:
                data = in_file.read()
            if not is_two_file:
                data = re.split('(\n\n|\r\n\r\n)', data, maxsplit=1)[-1]
            context = Context(hash(data))
            output = self.__formatData(data, context)
            out_file.write(output)
            self._write_deps(context, dest)

    def create_post(self, path, content=None, onefile=False, is_page=False, **kw):
        content = kw.pop('content', None)
        onefile = kw.pop('onefile', False)
        kw.pop('is_page', False)

        metadata = {}
        metadata.update(self.default_metadata)
        metadata.update(kw)
        makedirs(os.path.dirname(path))
        if not content.endswith('\n'):
            content += '\n'
        with io.open(path, "w+", encoding="utf8") as fd:
            if onefile:
                fd.write(write_metadata(metadata))
                fd.write('\n')
            fd.write(content)
