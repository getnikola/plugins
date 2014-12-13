# -*- coding: utf-8 -*-

# Copyright © 2014 Miguel Ángel García

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

from __future__ import unicode_literals, print_function

import os
import re
import datetime
import codecs

import six
from pprint import pprint

import yaml
from dateutil import parser as dateparser

from nikola.plugin_categories import Command
from nikola import utils
from nikola.plugins.basic_import import ImportMixin
from nikola.plugins.command.init import SAMPLE_CONF, prepare_config

LOGGER = utils.get_logger('import_jekyll', utils.STDERR_HANDLER)


class JekyllImportError(Exception):
    def __init__(self, arg, *args, **kwargs):
        self._arg = arg
        super(JekyllImportError, self).__init__(*args, **kwargs)


class JekyllConfigurationNotFound(JekyllImportError):
    def __str__(self):
        return 'Jekyll configuration file was not found at %s' % self._arg


class CommandImportJekyll(Command, ImportMixin):
    """Import a Jekyll or Octopress blog."""

    name = "import_jekyll"
    needs_config = False
    doc_usage = "[options] jekyll_site"
    doc_purpose = "import a Jekyll or Octopress site"

    _jekyll_config = None
    _jekyll_path = None
    _url_slug_mapping_file = None

    def _execute(self, options, args):
        """Import a Jekyll/Octopress site."""
        # Configuration
        self.import_into_existing_site = False

        # Parse args
        self._jekyll_path = args[0] if args else '.'
        self._url_slug_mapping_file = options['url_slug_file']
        self.output_folder = options['output_folder']

        # Execute
        try:
            self._read_config()
            self._write_site()
            self._import_posts()
        except JekyllImportError as e:
            LOGGER.error('ERROR: %s' % e)

    def _read_config(self):
        path = os.path.join(self._jekyll_path, '_config.yml')
        if not os.path.exists(path):
            raise JekyllConfigurationNotFound(path)

        LOGGER.debug('Loading Jekyll configuration file %s', path)
        with open(path) as fd:
            self._jekyll_config = yaml.load(fd.read())

    def _write_site(self):
        context = SAMPLE_CONF.copy()

        context['DEFAULT_LANG'] = 'en'
        context['BLOG_TITLE'] = self._jekyll_config.get('title', 'EXAMPLE')

        context['BLOG_DESCRIPTION'] = self._jekyll_config.get('description') or ''
        context['SITE_URL'] = self._jekyll_config.get('url', 'EXAMPLE')
        context['BLOG_EMAIL'] = self._jekyll_config.get('email') or ''
        context['BLOG_AUTHOR'] = self._jekyll_config.get('author') or ''
        context['POSTS'] = '''(
            ("posts/*.md", "posts", "post.tmpl"),
            ("posts/*.rst", "posts", "post.tmpl"),
            ("posts/*.txt", "posts", "post.tmpl"),
            ("posts/*.html", "posts", "post.tmpl"),
            )'''
        context['PAGES'] = '''(
            ("articles/*.txt", "articles", "story.tmpl"),
            ("articles/*.rst", "articles", "story.tmpl"),
            )'''
        context['COMPILERS'] = '''{
            "rest": ('.txt', '.rst'),
            "markdown": ('.md', '.mdown', '.markdown', '.wp'),
            "html": ('.html', '.htm')
            }
            '''

        if 'disqus_short_name' in self._jekyll_config:
            context['COMMENT_SYSTEM'] = 'disqus'
            context['COMMENT_SYSTEM_ID'] = self._jekyll_config[
                'disqus_short_name']

        conf_template = self.generate_base_site()
        conf_out_path = self.get_configuration_output_path()

        conf_template_render = conf_template.render(**prepare_config(context))
        self.write_configuration(conf_out_path, conf_template_render)

    def _import_posts(self):
        rel_path = self._jekyll_config.get('source', 'source')
        posts_path = os.path.join(self._jekyll_path, rel_path, '_posts')
        importer = JekyllPostImport()

        for dirpath, dirnames, filenames in os.walk(posts_path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if not filepath.lower().endswith(
                        ('.md', '.markdown', '.html', 'rst', '.textile')):
                    LOGGER.warning('Unknown format for file %s. Ignoring it!'
                                   % filepath)
                    continue
                LOGGER.info('Importing post %s' % filepath)
                output_relfile, nikola_post = importer.import_file(filepath)
                output_file = os.path.join(self.output_folder, 'posts',
                                           output_relfile)
                utils.makedirs(os.path.dirname(output_file))
                with codecs.open(output_file, 'w', encoding='utf-8') as fd:
                    fd.write(nikola_post)
                LOGGER.info('Writing post %s' % output_file)


class JekyllPostImport(object):
    def import_file(self, path):
        jmetadata, jcontent = self._split_metadata(path)
        metadata = self._import_metadata(path, jmetadata)
        doc = self._import_content(path, jcontent)

        filename = os.path.basename(path)
        date = metadata['date']
        output_file = os.path.join(str(date.year), str(date.month),
                               filename)

        content = self._serialize(metadata, doc, is_markdown(path))
        return output_file, content

    def _serialize(self, metadata, doc, is_markdown):
        header = ''
        keys = ('title', 'slug', 'date', 'description', 'category', 'tags')
        for key in keys:
            header += '.. %s: %s\n' % (key, metadata.get(key, ''))

        pattern = '<!--\n%s\n-->\n%s' if is_markdown else '%s\n%s'

        return pattern % (header, doc)

    def _split_metadata(self, path):
        with codecs.open(path, encoding='utf-8') as fd:
            post_content = fd.read()
        metadata = next(yaml.load_all(post_content))

        composer_iter = yaml.compose_all(post_content)
        composer = next(composer_iter)
        last_line = composer.end_mark.line + 1
        content = '\n'.join(post_content.splitlines()[last_line:])

        return metadata, content

    def _import_metadata(self, path, jmetadata):
        def extract_date():
            raw_date = jmetadata.get('date')
            if isinstance(raw_date, datetime.date):
                return raw_date
            if isinstance(raw_date, str):
                return dateparser.parse(raw_date)

            # date not in metadata or unreadable. Trying from filename.
            raw_date = re.findall(r'\d+\-\d+\-\d+', path)
            if raw_date:
                return dateparser.parse(raw_date[-1])
                logger.warning('Unknown date "%s". Using today.', raw_date)
            return datetime.date.today()

        def extract_title():
            if 'title' in jmetadata:
                return jmetadata['title']
            regex = (
                r'(?:\d+-\d+-\d+-)'
                r'(?P<name>.+?)'
                r'(?:\.\w+)?$'
            )
            m = re.match(regex, path)
            if m is None:
                return None
                name = m.group('name')
            return name

        tags = [x for x in jmetadata.get('tags') or [] if x]
        categories = [x for x in jmetadata.get('categories') or [] if x]
        return dict(
            title=extract_title(),
            slug=slugify_file(path),
            date=extract_date(),
            description=jmetadata.get('description') or '',
            tags=','.join(tags + categories),
            category=(categories[0] if categories else ''),
        )

    def _import_content(self, path, content):
        def replace_teaser_mark(content):
            REGEX_TEASER_MD = r'<!--\s*more\s*-->'
            REGEX_TEASER = r'..\s+more'
            if is_markdown(path):
                regex = REGEX_TEASER_MD
                repl = '<!-- TEASER_END -->'
            else:
                regex = REGEX_TEASER
                repl = '.. TEASER_END'
            return re.sub(
                regex,
                repl,
                content,
                count=1,
            )

        def replace_code(content):
            def code_surround(lang, code):
                return '.. code::%s\n%s' % (
                    ' %s' % lang if lang else '',
                    '\n'.join(('    ' + s if s.strip() else '')
                              for s in code.splitlines())
                )

            def code_repl(matchobj):
                lang = matchobj.group('lang')
                code = matchobj.group('code')
                return code_surround(lang, code)
            REGEX_CODE = (
                r'\{%\s*highlight\s*(?P<lang>\w+)?'
                r'(?P<props>\s*(?:linenos|linenos=\w+|hl_lines|hl_lines=\S+))*\s*%\}'
                r'(?P<code>.*?)'
                r'\{%\s*endhighlight\s*%\}'
            )
            return re.sub(REGEX_CODE, code_repl, content,
                          flags=re.MULTILINE | re.DOTALL)

        def replace_links(content):
            def link_repl(matchobj):
                url = matchobj.group('url')
                slug = slugify_file(url)
                return 'link://slug/{0}'.format(slug)
            REGEX_LINK = (
                r'{%' r'\s*'
                r'post_url' r'\s*'
                r'(?P<url>.*?)' r'\s*'
                r'%}'
            )
            return re.sub(REGEX_LINK, link_repl, content)

        for repl in (replace_code, replace_links):
            content = repl(content)
        return content


def slugify_file(filename):
    name, _ = os.path.splitext(os.path.basename(filename))
    if not isinstance(name, unicode):
        name = name.decode('unicode-escape')
    return utils.slugify(name)


def is_markdown(path):
    return path.lower().endswith(('.md', '.markdown'))


def is_textile(path):
    return path.lower().endswith(('.textile', ))
