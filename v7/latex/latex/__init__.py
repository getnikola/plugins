# -*- coding: utf-8 -*-

# Copyright © 2014-2017 Felix Fontein
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

"""Compile a subset of LaTeX to HTML."""

from __future__ import unicode_literals

import os
import io
import nikola.plugin_categories
import nikola.utils
import re
import json

from . import parser, htmlify

LOGGER = nikola.utils.get_logger('compile_latex', nikola.utils.STDERR_HANDLER)


class LaTeXContext(object):
    """Represent a context for LaTeX post compilation.

    Allows to add dependencies, store data, and resolve links.
    """

    id = None

    def __init__(self, id, lang, thm_names, name=None):
        """Initialize context."""
        self.id = id
        self.name = name
        self.lang = lang
        self.thm_names = thm_names
        self.__file_deps_fragment = set()
        self.__file_deps_page = set()
        self.__uptodate_deps_fragment = list()
        self.__uptodate_deps_page = list()
        self.__plugin_data = {}
        self.__link_providers = []

    def get_name(self):
        """Return name associated to context."""
        return '(unknown:{0})'.format(self.id) if self.name is None else self.name

    def add_file_dependency(self, filename, add='both'):
        """Add file dependency to post. Similar to Post.add_file_dependency."""
        if add not in {'fragment', 'page', 'both'}:
            raise Exception("Add parameter is '{0}', but must be either 'fragment', 'page', or 'both'.".format(add))
        if add == 'fragment' or add == 'both':
            self.__file_deps_fragment.add(filename)
        if add == 'page' or add == 'both':
            self.__file_deps_page.add(filename)

    def add_uptodate_dependency(self, name, uptodate_dependency, add='both'):
        """Add doit uptodate dependency to post. Similar to Post.add_uptodate_dependency."""
        if add not in {'fragment', 'page', 'both'}:
            raise Exception("Add parameter is '{0}', but must be either 'fragment', 'page', or 'both'.".format(add))
        if add == 'fragment' or add == 'both':
            self.__uptodate_deps_fragment.append({'name': name, 'deps': uptodate_dependency})
        if add == 'page' or add == 'both':
            self.__uptodate_deps_page.append({'name': name, 'deps': uptodate_dependency})

    def add_link_provider(self, link_provider):
        """Add a link provider to the context."""
        self.__link_providers.append(link_provider)

    def has_dependencies(self):
        """Check whether dependencies are available."""
        return (len(self.__file_deps_fragment) > 0 or len(self.__file_deps_page) > 0 or
                len(self.__uptodate_deps_fragment) > 0 or len(self.__uptodate_deps_page) > 0)

    def get_file_dependencies_fragment(self):
        """Retrieve file dependencies for fragment generation."""
        return sorted(list(self.__file_deps_fragment))

    def get_file_dependencies_page(self):
        """Retrieve file dependencies for page generation."""
        return sorted(list(self.__file_deps_page))

    def get_uptodate_dependencies_fragment(self):
        """Retrieve doit uptodate dependencies for fragment generation."""
        return self.__uptodate_deps_fragment

    def get_uptodate_dependencies_page(self):
        """Retrieve doit uptodate dependencies for page generation."""
        return self.__uptodate_deps_page

    def store_plugin_data(self, plugin_name, key, data):
        """Store plugin-specific data in context."""
        if plugin_name not in self.__plugin_data:
            self.__plugin_data[plugin_name] = {}
        self.__plugin_data[plugin_name][key] = data

    def get_plugin_data(self, plugin_name, key, default_value=None):
        """Retrieve plugin-specific data from context."""
        plugin_data = self.__plugin_data.get(plugin_name)
        return default_value if plugin_data is None else plugin_data.get(key, default_value)

    def inc_plugin_counter(self, plugin_name, key):
        """Provide simple plugin-specific counter for plugin to access."""
        counter = self.get_plugin_data(plugin_name, key, 0) + 1
        self.store_plugin_data(plugin_name, key, counter)
        return counter

    def __str__(self):
        """Return string representation."""
        return 'LaTeXContext<{0}>({1}, {2}, {3}, {4})'.format(self.id, self.__file_deps_fragment, self.__file_deps_page, self.__uptodate_deps_fragment, self.__uptodate_deps_page)

    def provide_link(self, reference):
        """Resolve link to reference. Returns pair (URL, label)."""
        idx = reference.find('::')
        if idx < 0:
            return '#{0}'.format(reference), reference
        else:
            site, label = reference[:idx], reference[idx + len('::'):]
            for link_provider in self.__link_providers:
                result = link_provider.provide_link(site, label, self.lang)
                if result is not None:
                    return result
            raise Exception("Cannot provide link for site '{0}' with label '{1}'!".format(site, label))


class CompileLaTeX(nikola.plugin_categories.PageCompiler):
    """Compiles a subset of LaTeX into HTML."""

    name = 'latex'
    demote_headers = True
    use_dep_files = False

    def __init__(self):
        """Create page compiler object."""
        super(CompileLaTeX, self).__init__()
        self.__beautify = True
        self.__parsing_environment = parser.ParsingEnvironment()
        self.__link_providers = {}

    def set_site(self, site):
        """Set Nikola site object."""
        super(CompileLaTeX, self).set_site(site)

        # Classify plugins
        renderer_plugins = {}
        other_plugins = {}
        for plugin in self.get_compiler_extensions():
            try:
                if plugin.plugin_object.latex_plugin_type == 'formula_renderer':
                    LOGGER.debug('Found LaTeX formula renderer plugin {0}'.format(plugin.name))
                    renderer_plugins[plugin.name] = plugin
                else:
                    LOGGER.warn('Found unknown LaTeX page compiler plugin {0}!'.format(plugin.name))
                    other_plugins[plugin.name] = plugin
                plugin.plugin_object.initialize(self, self.__parsing_environment)
            except Exception:
                LOGGER.error('Found broken LaTeX page compiler plugin {0}!'.format(plugin.name))

        # Look for formula renderer
        renderer_name = site.config.get('LATEX_FORMULA_RENDERER', 'latex_formula_image_renderer')
        if renderer_name not in renderer_plugins:
            raise Exception("Unknown formula renderer '{}'!".format(renderer_name))
        self.__formula_renderer = renderer_plugins[renderer_name].plugin_object
        self.__formula_renderer_name = renderer_name
        self.__plugins = list(other_plugins.values())
        self.__all_plugins = [self.__formula_renderer] + self.__plugins

        # Configure plugins
        for plugin in self.__all_plugins:
            plugin.initialize(self, self.__parsing_environment)

    def _get_dep_filename(self, post, lang):
        """Retrieve dependency filename."""
        return post.translated_base_path(lang) + '.ltxdep'

    def get_extra_targets(self, post, lang, dest):
        """Retrieve extra targets generated by page compiler."""
        result = [self._get_dep_filename(post, lang)]
        for plugin in self.__all_plugins:
            result += plugin.get_extra_targets(post, lang, dest)
        return result

    def _read_extra_deps(self, post, lang):
        """Read extra dependencies from JSON file."""
        dep_path = self._get_dep_filename(post, lang)
        if os.path.isfile(dep_path):
            with io.open(dep_path, 'rb') as file:
                result = json.loads(file.read().decode('utf-8'))
            if isinstance(result, list) and len(result) == 4:
                return result
        return ([], [], [], [])

    def _add_extra_deps(self, post, lang, what, where):
        """Return a list of extra dependencies for given post and language.

        ``what`` can be ``file`` or ``uptodate`` and describes what kind
        of dependency can be added, and ``where`` can be ``fragment`` or
        ``page`` and describes where the dependency will be added.
        """
        result = []
        # Get dependencies from disk
        idx = 1 if where == 'fragment' else 0
        if what == 'uptodate':
            for uptodate_data in self._read_extra_deps(post, lang)[2 + idx]:
                result.append(nikola.utils.config_changed(uptodate_data['deps'], uptodate_data['name']))
        else:
            result.extend(self._read_extra_deps(post, lang)[0 + idx])
        # Add own dependencies
        if what == 'uptodate' and where == 'fragment':
            result.append(nikola.utils.config_changed({
                'formula_renderer': self.__formula_renderer_name,
                'theorem_names': self._get_theorem_names(lang),
            }, 'latex_page_compiler:config'))
        # Add plugin dependencies
        for plugin in self.__all_plugins:
            result.extend(plugin.add_extra_deps(post, lang, what, where))
        return result

    def register_extra_dependencies(self, post):
        """Register extra dependencies extractor."""
        def register(lang, where):
            """Create language- and where-dependent extractors."""
            post.add_dependency(lambda: self._add_extra_deps(post, lang, 'file', where), where, lang=lang)
            post.add_dependency_uptodate(lambda: self._add_extra_deps(post, lang, 'uptodate', where), True, where, lang=lang)

        for lang in self.site.config['TRANSLATIONS']:
            for where in ['fragment', 'page']:
                register(lang, where)

    def get_parsing_environment(self):
        """Retrieve parsing environment. See ``parser.ParsingEnvironment`` for documentation."""
        return self.__parsing_environment

    def _format_data(self, data, latex_context):
        """Parse and HTMLify data from string, given LaTeX context."""
        tree = parser.parse(data, self.__parsing_environment, filename=latex_context.name)
        result = htmlify.HTMLify(tree, self.__formula_renderer, latex_context, beautify=self.__beautify, outer_indent=0)
        for plugin in self.__all_plugins:
            result = plugin.modify_html_output(result, latex_context)
        return result

    def _get_theorem_names(self, lang):
        """Get language-dependent theorem environment names from messages."""
        thm_names = {}
        for name in ['thm_name', 'prop_name', 'cor_name', 'lemma_name', 'def_name', 'defs_name', 'proof_name', 'example_name', 'examples_name', 'remark_name', 'remarks_name']:
            thm_names[name] = self.site.MESSAGES('math_{0}'.format(name), lang)
        return thm_names

    def _compile_string_impl(self, data, source_path=None, is_two_file=True, post=None, lang=None, link_providers=None):
        """Compile to string implementation."""
        try:
            if not is_two_file:
                data = re.split('(\n\n|\r\n\r\n)', data, maxsplit=1)[-1]
            latex_context = LaTeXContext(hash(data), lang=lang, thm_names=self._get_theorem_names(lang), name=source_path)
            if link_providers:
                for link_provider in link_providers:
                    latex_context.add_link_provider(link_provider)
            for plugin in self.__all_plugins:
                plugin.before_processing(latex_context, source_path, post)
            output = self._format_data(data, latex_context)
            for plugin in self.__all_plugins:
                plugin.after_processing(latex_context, source_path, post)
            return (output, latex_context, [])  # last part are shortcode dependencies
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise e

    def compile_string(self, data, source_path=None, is_two_file=True, post=None, lang=None):
        """Compile the source file into HTML strings."""
        if lang is None:
            lang = nikola.utils.LocaleBorg().current_lang
        return self._compile_string_impl(data, source_path=source_path, is_two_file=is_two_file, post=post, lang=lang)

    def compile_to_string(self, source_data, name=None):
        """Old, deprecated interface."""
        return self._compile_string_impl(source_data, source_path=name, lang=nikola.utils.LocaleBorg().current_lang)[0]

    def _write_deps(self, latex_context, deps_path):
        """Write dependencies into JSON file."""
        data = (latex_context.get_file_dependencies_fragment(), latex_context.get_file_dependencies_page(),
                latex_context.get_uptodate_dependencies_fragment(), latex_context.get_uptodate_dependencies_page())
        with io.open(deps_path, 'wb') as file:
            file.write(json.dumps(data).encode('utf-8'))

    def add_link_provider(self, source, link_provider):
        """Add link provider to plugin. Will be added to LaTeX contexts automatically."""
        if source not in self.__link_providers:
            self.__link_providers[source] = []
        self.__link_providers[source].append(link_provider)

    def compile(self, source, dest, is_two_file=True, post=None, lang=None):
        """Compile the source, save it on dest."""
        nikola.utils.makedirs(os.path.dirname(dest))
        if lang is None:
            lang = nikola.utils.LocaleBorg().current_lang
        try:
            with io.open(dest, 'w+', encoding='utf8') as out_file:
                with io.open(source, 'r', encoding='utf8') as in_file:
                    data = in_file.read()
                output, latex_context, _ = self._compile_string_impl(data, source_path=source, is_two_file=is_two_file, post=post,
                                                                     lang=lang, link_providers=self.__link_providers.get(source))
                # Write post
                out_file.write(output)
                # Write dependencies
                if post is None:
                    deps_path = dest + '.wpdep'
                else:
                    deps_path = self._get_dep_filename(post, lang)
                self._write_deps(latex_context, deps_path)
                # Add dependencies and write formulae info
                if post is not None:
                    for fn in latex_context.get_file_dependencies_fragment():
                        post.add_dependency(fn, add='fragment', lang=lang)
                    for fn in latex_context.get_file_dependencies_page():
                        post.add_dependency(fn, add='page', lang=lang)
                    for uptodate_data in latex_context.get_uptodate_dependencies_fragment():
                        post.add_dependency_uptodate(nikola.utils.config_changed(uptodate_data['deps'], uptodate_data['name']), add='fragment', lang=lang)
                    for uptodate_data in latex_context.get_uptodate_dependencies_page():
                        post.add_dependency_uptodate(nikola.utils.config_changed(uptodate_data['deps'], uptodate_data['name']), add='page', lang=lang)
                    for plugin in self.__all_plugins:
                        plugin.write_extra_targets(post, lang, dest, latex_context)
        except Exception:
            # If an exception was raised, remove output file and re-raise it
            try:
                os.unlink(dest)
            except Exception:
                pass
            raise

    def create_post(self, path, content=None, onefile=False, is_page=False, **kw):
        """Create empty post."""
        metadata = {}
        metadata.update(self.default_metadata)
        metadata.update(kw)
        nikola.utils.makedirs(os.path.dirname(path))
        if not content.endswith('\n'):
            content += '\n'
        with io.open(path, 'w+', encoding='utf8') as fd:
            if onefile:
                fd.write(nikola.utils.write_metadata(metadata))
                fd.write('\n\n')
            fd.write(content)
