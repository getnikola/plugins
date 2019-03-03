# -*- coding: utf-8 -*-

# Copyright © 2017-2019, Chris Warrick and others.

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

"""Generate JSON Feeds."""

import json
import io
import os
import lxml

from nikola.plugin_categories import Task
from nikola import utils

from urllib.parse import urljoin


class JSONFeed(Task):
    """Generate JSON feeds."""

    name = "jsonfeed"
    supported_taxonomies = {
        'archive': 'archive_jsonfeed',
        'author': 'author_jsonfeed',
        'category': 'category_jsonfeed',
        'tag': 'tag_jsonfeed',
    }
    _section_archive_link_warned = False

    def set_site(self, site):
        """Set site, which is a Nikola instance."""
        super(JSONFeed, self).set_site(site)

        self.kw = {
            'feed_links_append_query': self.site.config['FEED_LINKS_APPEND_QUERY'],
            'feed_length': self.site.config['FEED_LENGTH'],
            'feed_plain': self.site.config['FEED_PLAIN'],
            'feed_read_more_link': self.site.config['FEED_READ_MORE_LINK'],
            'feed_teasers': self.site.config['FEED_TEASERS'],
            'jsonfeed_append_links': self.site.config.get('JSONFEED_APPEND_LINKS', True),
            'site_url': self.site.config['SITE_URL'],
            'blog_title': self.site.config['BLOG_TITLE'],
            'blog_description': self.site.config['BLOG_DESCRIPTION'],
            'blog_author': self.site.config['BLOG_AUTHOR'],
            'tag_titles': self.site.config['TAG_TITLES'],
            'category_titles': self.site.config['CATEGORY_TITLES'],
            'archives_are_indexes': self.site.config['ARCHIVES_ARE_INDEXES'],
        }

        self.site.register_path_handler("index_jsonfeed", self.index_jsonfeed_path)
        for t in self.supported_taxonomies.values():
            self.site.register_path_handler(t, getattr(self, t + '_path'))

        # Add links if desired
        if self.kw['jsonfeed_append_links']:
            self.site.template_hooks['extra_head'].append(self.jsonfeed_html_link, True)

    def gen_tasks(self):
        """Generate JSON feeds."""
        self.site.scan_posts()
        yield self.group_task()

        for lang in self.site.translations:
            # Main feed
            title = self.kw['blog_title'](lang)
            link = self.kw['site_url']
            description = self.kw['blog_description'](lang)
            timeline = self.site.posts[:self.kw['feed_length']]
            output_name = os.path.normpath(os.path.join(self.site.config['OUTPUT_FOLDER'], self.site.path("index_jsonfeed", "", lang)))
            feed_url = self.get_link("index_jsonfeed", "", lang)

            yield self.generate_feed_task(lang, title, link, description,
                                          timeline, feed_url, output_name)

            for classification_name, path_handler in self.supported_taxonomies.items():
                taxonomy = self.site.taxonomy_plugins[classification_name]

                if classification_name == "archive" and not self.kw['archives_are_indexes']:
                    continue

                classification_timelines = {}
                for tlang, posts_per_classification in self.site.posts_per_classification[taxonomy.classification_name].items():
                    if lang != tlang and not taxonomy.also_create_classifications_from_other_languages:
                        continue
                    classification_timelines.update(posts_per_classification)

                for classification, timeline in classification_timelines.items():
                    if not classification:
                        continue
                    if taxonomy.has_hierarchy:
                        node = self.site.hierarchy_lookup_per_classification[taxonomy.classification_name][lang][classification]
                        taxo_context = taxonomy.provide_context_and_uptodate(classification, lang, node)[0]
                    else:
                        taxo_context = taxonomy.provide_context_and_uptodate(classification, lang)[0]
                    title = taxo_context.get('title', classification)
                    link = self.get_link(classification_name, classification, lang)
                    description = taxo_context.get('description', self.kw['blog_description'](lang))
                    timeline = timeline[:self.kw['feed_length']]
                    output_name = os.path.normpath(os.path.join(self.site.config['OUTPUT_FOLDER'], self.site.path(path_handler, classification, lang)))
                    feed_url = self.get_link(path_handler, classification, lang)

                    # Special handling for author pages
                    if classification_name == "author":
                        primary_author = {
                            'name': classification,
                            'url': link
                        }
                    else:
                        primary_author = None

                    yield self.generate_feed_task(lang, title, link, description,
                                                  timeline, feed_url, output_name, primary_author)

    def index_jsonfeed_path(self, name, lang, **kwargs):
        """Return path to main JSON Feed."""
        return [_f for _f in [self.site.config['TRANSLATIONS'][lang], 'feed.json'] if _f]

    def archive_jsonfeed_path(self, name, lang, **kwargs):
        """Return path to archive JSON Feed."""
        return [_f for _f in [self.site.config['TRANSLATIONS'][lang],
                              self.site.config['ARCHIVE_PATH'](lang), name, 'feed.json'] if _f]

    def author_jsonfeed_path(self, name, lang, **kwargs):
        """Return path to author JSON Feed."""
        if self.site.config['SLUG_AUTHOR_PATH']:
            filename = utils.slugify(name, lang) + '-feed.json'
        else:
            filename = name + '-feed.json'
        return [_f for _f in [self.site.config['TRANSLATIONS'][lang],
                              self.site.config['AUTHOR_PATH'](lang), filename] if _f]

    def category_jsonfeed_path(self, name, lang, **kwargs):
        """Return path to category JSON Feed."""
        t = self.site.taxonomy_plugins['category']
        name = t.slugify_category_name(t.extract_hierarchy(name), lang)[0]
        return [_f for _f in [self.site.config['TRANSLATIONS'][lang],
                              self.site.config['CATEGORY_PATH'](lang), name + '-feed.json'] if _f]

    def section_index_jsonfeed_path(self, name, lang, **kwargs):
        """Return path to section JSON Feed."""
        return [_f for _f in [self.site.config['TRANSLATIONS'][lang],
                              self.site.config['SECTION_PATH'](lang), name, 'feed.json'] if _f]

    def tag_jsonfeed_path(self, name, lang, **kwargs):
        """Return path to tag JSON Feed."""
        t = self.site.taxonomy_plugins['tag']
        name = t.slugify_tag_name(name, lang)
        return [_f for _f in [self.site.config['TRANSLATIONS'][lang],
                              self.site.config['TAG_PATH'](lang), name + '-feed.json'] if _f]

    def get_link(self, path_handler, classification, lang):
        """Get link for a page."""
        return urljoin(self.site.config['BASE_URL'], self.site.link(path_handler, classification, lang).lstrip('/'))

    def jsonfeed_html_link(self, site, context):
        """Generate HTML fragment with link to JSON feed."""
        if 'pagekind' not in context:
            return ''
        pagekind = context['pagekind']
        lang = context['lang']
        fragment = '<link rel="alternate" type="application/json" title="{title}" href="{url}">\n'
        if 'main_index' in pagekind:
            path_handler = "index_jsonfeed"
            name = ""
        elif 'author_page' in pagekind:
            path_handler = "author_jsonfeed"
            name = context["author"]
        elif 'tag_page' in pagekind:
            path_handler = context["kind"] + "_jsonfeed"
            name = context[context["kind"]]
        elif 'archive_page' in pagekind:
            path_handler = "archive_jsonfeed"
            if "archive_name" in context:
                name = context["archive_name"]
            else:
                if not self._section_archive_link_warned:
                    utils.LOGGER.warning("To create links for section and archive JSON feeds, you need Nikola >= 7.8.6.")
                    self._section_archive_link_warned = True
                return ''
        elif 'section_page' in pagekind:
            path_handler = "section_index_jsonfeed"
            if "section" in context:
                name = context["section"]
            else:
                if not self._section_archive_link_warned:
                    utils.LOGGER.warning("To create links for section and archive JSON feeds, you need Nikola >= 7.8.6.")
                    self._section_archive_link_warned = True
                return ''
        else:
            return ''  # Do nothing on unsupported pages

        if len(self.site.translations) > 1:
            out = ""
            for lang in self.site.translations:
                title = "JSON Feed ({0})".format(lang)
                url = self.site.link(path_handler, name, lang)
                out += fragment.format(title=title, url=url)
            return out
        else:
            title = "JSON Feed"
            url = self.site.link(path_handler, name, lang)
            return fragment.format(title=title, url=url)

    def generate_feed_task(self, lang, title, link, description, timeline,
                           feed_url, output_name, primary_author=None):
        """Generate a task to create a feed."""
        # Build dependency list
        deps = []
        deps_uptodate = []
        for post in timeline:
            deps += post.deps(lang)
            deps_uptodate += post.deps_uptodate(lang)

        task = {
            'basename': str(self.name),
            'name': str(output_name),
            'targets': [output_name],
            'file_dep': deps,
            'task_dep': ['render_posts', 'render_taxonomies'],
            'actions': [(self.generate_feed, (lang, title, link, description,
                                              timeline, feed_url, output_name,
                                              primary_author))],
            'uptodate': [utils.config_changed(self.kw, 'jsonfeed:' + output_name)] + deps_uptodate,
            'clean': True
        }

        yield utils.apply_filters(task, self.site.config['FILTERS'])

    def generate_feed(self, lang, title, link, description, timeline,
                      feed_url, output_name, primary_author=None):
        """Generate a feed and write it to file."""
        utils.LocaleBorg().set_locale(lang)
        items = []
        for post in timeline:
            item = {
                "id": post.guid(lang),
                "url": post.permalink(lang),
                "title": post.title(lang),
                "date_published": post.date.replace(microsecond=0).isoformat(),
                "date_modified": post.updated.replace(microsecond=0).isoformat(),
                "author": {
                    "name": post.author(lang),
                    "url": self.site.link("author", post.author(lang), lang)
                },
                "tags": post.tags_for_language(lang),
            }

            if post.updated == post.date:
                del item["date_modified"]

            link = post.meta[lang].get('link')
            if link:
                item['external_url'] = link

            previewimage = post.meta[lang].get('previewimage')
            if previewimage:
                item['image'] = self.site.url_replacer(post.permalink(), previewimage, lang, 'absolute')

            if self.kw['feed_plain']:
                strip_html = True
                content_tag = "content_text"
            else:
                strip_html = False
                content_tag = "content_html"

            data = post.text(lang, self.kw['feed_teasers'], strip_html, True, True, self.kw['feed_links_append_query'])

            if feed_url is not None and data:
                # Copied from nikola.py
                # Massage the post's HTML (unless plain)
                if not strip_html:
                    if 'previewimage' in post.meta[lang] and post.meta[lang]['previewimage'] not in data:
                        data = "<figure><img src=\"{}\"></figure> {}".format(post.meta[lang]['previewimage'], data)
                    # FIXME: this is duplicated with code in Post.text()
                    try:
                        doc = lxml.html.document_fromstring(data)
                        doc.rewrite_links(lambda dst: self.site.url_replacer(post.permalink(), dst, lang, 'absolute'))
                        try:
                            body = doc.body
                            data = (body.text or '') + ''.join(
                                [lxml.html.tostring(child, encoding='unicode')
                                 for child in body.iterchildren()])
                        except IndexError:  # No body there, it happens sometimes
                            data = ''
                    except lxml.etree.ParserError as e:
                        if str(e) == "Document is empty":
                            data = ""
                        else:  # let other errors raise
                            raise

            item[content_tag] = data
            items.append(item)

        if not primary_author:
            # Override for author pages
            primary_author = {"name": self.kw['blog_author'](lang)}

        feed = {
            "version": "https://jsonfeed.org/version/1",
            "user_comment": ("This feed allows you to read the posts from this "
                             "site in any feed reader that supports the JSON "
                             "Feed format. To add " "this feed to your reader, "
                             "copy the following URL — " + feed_url +
                             " — and add it your reader."),
            "title": title,
            "home_page_url": self.kw['site_url'],
            "feed_url": feed_url,
            "description": description,
            "author": primary_author,
            "items": items
        }

        utils.makedirs(os.path.dirname(output_name))

        with io.open(output_name, 'w', encoding='utf-8') as fh:
            json.dump(feed, fh, ensure_ascii=False, indent=4)
