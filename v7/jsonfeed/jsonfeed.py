# -*- coding: utf-8 -*-

# Copyright © 2017, Chris Warrick and others.

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

from __future__ import unicode_literals
import lxml
import json
import io
import os

from nikola.plugin_categories import Task
from nikola import utils

try:
    from urlparse import urljoin
except ImportError:
    from urllib.parse import urljoin  # NOQA


class JSONFeed(Task):
    """Generate JSON feeds."""

    name = "jsonfeed"

    def set_site(self, site):
        """Set site, which is a Nikola instance."""
        super(JSONFeed, self).set_site(site)

        self.kw = {
            'feed_links_append_query': self.site.config['FEED_LINKS_APPEND_QUERY'],
            'feed_length': self.site.config['FEED_LENGTH'],
            'feed_plain': self.site.config['FEED_PLAIN'],
            'feed_previewimage': self.site.config['FEED_PREVIEWIMAGE'],
            'feed_read_more_link': self.site.config['FEED_READ_MORE_LINK'],
            'feed_teasers': self.site.config['FEED_TEASERS'],
            'jsonfeed_append_links': self.site.config.get('JSONFEED_APPEND_LINKS', True),
            'site_url': self.site.config['SITE_URL'],
            'blog_title': self.site.config['BLOG_TITLE'],
            'blog_description': self.site.config['BLOG_DESCRIPTION'],
            'blog_author': self.site.config['BLOG_AUTHOR'],
        }

        self.site.register_path_handler("index_jsonfeed", self.index_jsonfeed_path)

    def gen_tasks(self):
        """Generate JSON feeds."""
        self.site.scan_posts()
        yield self.group_task()

        # Main feed
        for lang in self.site.translations:
            title = self.kw['blog_title'](lang)
            link = self.kw['site_url']
            output_name = os.path.normpath(os.path.join(self.site.config['OUTPUT_FOLDER'], self.site.path("index_jsonfeed", "", lang)))
            feed_url = urljoin(self.site.config['BASE_URL'], self.site.link("index_jsonfeed", "", lang).lstrip('/'))
            description = self.kw['blog_description'](lang)
            timeline = self.site.posts[:self.kw['feed_length']]
            yield self.generate_feed_task(lang, title, link, description,
                                          timeline, feed_url, output_name)

    def index_jsonfeed_path(self, name, lang, **kwargs):
        """Return path to main JSON Feed."""
        return [_f for _f in [self.site.config['TRANSLATIONS'][lang], 'feed.json'] if _f]

    def generate_feed_task(self, lang, title, link, description, timeline,
                           feed_url, output_name, primary_author=None):
        """Generate a task to create a feed."""
        task = {
            'basename': str(self.name),
            'name': str(output_name),
            'targets': [output_name],
            'file_dep': sorted([_.base_path for _ in timeline]),
            'task_dep': ['render_posts'],
            'actions': [(self.generate_feed, (lang, title, link, description,
                                              timeline, feed_url, output_name,
                                              primary_author))],
            'uptodate': [utils.config_changed(self.kw, 'jsonfeed:' + output_name)],
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
                    if self.kw["feed_previewimage"] and 'previewimage' in post.meta[lang] and post.meta[lang]['previewimage'] not in data:
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
                            raise(e)

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

        with io.open(output_name, 'w', encoding='utf-8') as fh:
            json.dump(feed, fh, ensure_ascii=False, indent=4)
