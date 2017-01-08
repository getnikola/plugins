# -*- coding: utf-8 -*-

# A WordPress compiler plugin for Nikola
#
# Copyright (C) 2014-2015 by Felix Fontein
# Copyright (C) by the WordPress contributors
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
import io
import json
import re
import sys

from nikola.plugin_categories import PageCompiler
from nikola.utils import makedirs, write_metadata, LocaleBorg
from nikola.utils import get_logger, STDERR_HANDLER

from . import default_filters, php, plugin_interface, shortcodes

_LOGGER = get_logger('compile_wordpress', STDERR_HANDLER)


class Context(object):
    id = None

    def __init__(self, id, name=None, additional_data=None):
        self.id = id
        self.name = name
        self.__file_deps_fragment = set()
        self.__file_deps_page = set()
        self.__uptodate_deps_fragment = list()
        self.__uptodate_deps_page = list()
        self.__additional_data = additional_data or {}
        self.__plugin_data = {}

    def get_name(self):
        return "(unknown:{0})".format(self.id) if self.name is None else self.name

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

    def get_additional_data(self, name):
        return self.__additional_data.get(name)

    def store_plugin_data(self, plugin_name, key, data):
        if plugin_name not in self.__plugin_data:
            self.__plugin_data[plugin_name] = {}
        self.__plugin_data[plugin_name][key] = data

    def get_plugin_data(self, plugin_name, key, default_value=None):
        plugin_data = self.__plugin_data.get(plugin_name)
        return default_value if plugin_data is None else plugin_data.get(key, default_value)

    def inc_plugin_counter(self, plugin_name, key):
        counter = self.get_plugin_data(plugin_name, key, 0)
        counter += 1
        self.store_plugin_data(plugin_name, key, counter)
        return counter

    def __str__(self):
        return "Context<" + str(self.id) + ">(" + str(self.__file_deps_fragment) + ", " + str(self.__file_deps_page) + ", " + str(self.__uptodate_deps_fragment) + ", " + str(self.__uptodate_deps_page) + ")"


class CompileWordpress(PageCompiler):
    """Compiles a subset of Wordpress into HTML."""

    name = "wordpress"
    demote_headers = True
    use_dep_files = False
    site = None

    def __init__(self):
        super(CompileWordpress, self).__init__()
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
        # collect plugins
        count = 0
        modules = {
            'default_filters': default_filters,
            'php': php,
            'plugin_interface': plugin_interface,
            'shortcodes': shortcodes,
            'wordpress': sys.modules[__name__]
        }
        for plugin in self.get_compiler_extensions():
            _LOGGER.info("Registered WordPress plugin {0}".format(plugin.name))
            plugin.plugin_object.register(self, modules)
            count += 1
        _LOGGER.info("Registered {0} WordPress plugin{1}".format(count, "s" if count != 1 else ""))

    def register_head_code(self, head_function):
        # FIXME: implement
        # (not even sure if it's really implementable...)
        raise NotImplementedError()

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
        super(CompileWordpress, self).set_site(site)
        self._register_plugins()

    def __formatData(self, data, context, source=None):
        output = self.filter("the_content", data, context)
        left_shortcodes = self.__shortcodes.get_containing_shortcodes_set(output)
        if len(left_shortcodes) > 0 and source is not None:
            _LOGGER.warning("The post '" + source + "' still contains shortcodes: " + str(left_shortcodes))
        return output

    def compile_string(self, data, source_path=None, is_two_file=True, post=None, lang=None):
        """New interface. Might be removed at some time."""
        context = Context(hash(source_data), name=source_path)
        html = self.__formatData(source_data, context)
        return (html, [])  # second part are shortcode dependencies

    def compile_to_string(self, source_data, name=None, additional_data=None):
        """Old interface. Might be removed at some time."""
        context = Context(hash(source_data), name=name, additional_data=additional_data)
        return self.__formatData(source_data, context)

    def _get_dep_filename(self, post, lang):
        return post.translated_base_path(lang) + '.wpdep'

    def get_extra_targets(self, post, lang, dest):
        return [self._get_dep_filename(post, lang)]

    def _read_extra_deps(self, post, lang):
        dep_path = self._get_dep_filename(post, lang)
        if os.path.isfile(dep_path):
            with io.open(dep_path, 'rb') as file:
                result = json.loads(file.read().decode('utf-8'))
            if type(result) == list and len(result) == 4:
                return result
        return ([], [], [], [])

    def register_extra_dependencies(self, post):
        def register(lang):
            post.add_dependency(lambda: self._read_extra_deps(post, lang)[0], 'fragment', lang=lang)
            post.add_dependency(lambda: self._read_extra_deps(post, lang)[1], 'page', lang=lang)
            post.add_dependency_uptodate(lambda: self._read_extra_deps(post, lang)[2], True, 'fragment', lang=lang)
            post.add_dependency_uptodate(lambda: self._read_extra_deps(post, lang)[3], True, 'page', lang=lang)

        for lang in self.site.config['TRANSLATIONS']:
            register(lang)

    def _write_deps(self, context, deps_path):
        data = (context.get_file_dependencies_fragment(), context.get_file_dependencies_page(),
                context.get_uptodate_dependencies_fragment(), context.get_uptodate_dependencies_page())
        with io.open(deps_path, "w+", encoding="utf8") as file:
            file.write(json.dumps(data))

    def _read_similar_file(self, source, suffix):
        path, filename = os.path.split(source)
        filename_parts = filename.split('.')
        for i in range(len(filename_parts), 0, -1):
            candidate = os.path.join(path, '.'.join(filename_parts[:i]) + suffix)
            try:
                with open(candidate, "rb") as in_file:
                    # _LOGGER.info("Found file {0} for {1}.".format(candidate, source))
                    return in_file.read(), candidate
            except:
                pass
        return None, None

    def load_additional_data(self, source):
        result = {}
        dependent_files = set()

        attachments, filename = self._read_similar_file(source, ".attachments.json")
        if attachments is not None:
            try:
                attachments = json.loads(attachments.decode('utf-8'))
                result['attachments'] = attachments
                dependent_files.add(filename)
            except Exception as e:
                _LOGGER.error("Could not load attachments for {0}! (Exception: {1})".format(source, e))

        return result, dependent_files

    def compile(self, source, dest, is_two_file=True, post=None, lang=None):
        if lang is None:
            lang = LocaleBorg().current_lang
        makedirs(os.path.dirname(dest))
        with io.open(dest, "w+", encoding="utf8") as out_file:
            # Read post
            with io.open(source, "r", encoding="utf8") as in_file:
                data = in_file.read()
            if not is_two_file:
                data = re.split('(\n\n|\r\n\r\n)', data, maxsplit=1)[-1]
            # Read additional data
            additional_data, dependent_files = self.load_additional_data(source)
            # Process post
            context = Context(hash(data), name=source, additional_data=additional_data)
            for filename in dependent_files:
                context.add_file_dependency(filename, 'fragment')
            output = self.__formatData(data, context)
            # Write result
            out_file.write(output)
            if post is None:
                deps_path = dest + '.wpdep'
            else:
                deps_path = self._get_dep_filename(post, lang)
            self._write_deps(context, deps_path)

    def compile_html(self, source, dest, is_two_file=False):
        self.compile(source, dest, is_two_file)

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
