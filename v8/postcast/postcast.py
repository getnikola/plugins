# -*- coding: utf-8 -*-

# Copyright © 2019 Jonathon Anderson
# Original speechsynthesizednetcast copyright © 2013–2014 Daniel Aleksandersen and others

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

import mimetypes
import os
import requests
try:
    from urlparse import urljoin, urlparse
except ImportError:
    from urllib.parse import urljoin, urlparse

from nikola.plugin_categories import Task

from nikola import utils


class Postcast (Task):
    """Generate an RSS podcast/netcast from posts."""

    doc_purpose = "Generate an RSS podcast/netcast from posts."

    logger = None

    name = 'postcast'

    def gen_tasks(self):
        config = self.site.config

        self.logger = utils.get_logger('postcast')

        self.site.scan_posts()
        yield self.group_task()

        for slug in config.get('POSTCASTS', []):
            category = _get_with_default_key(
                config.get('POSTCAST_CATEGORY', {}), slug, '')
            tags = _get_with_default_key(
                config.get('POSTCAST_TAGS', {}), slug, '')
            itunes_explicit = _get_with_default_key(
                config.get('POSTCAST_ITUNES_EXPLICIT', {}), slug, '')
            itunes_image = _get_with_default_key(
                config.get('POSTCAST_ITUNES_IMAGE', {}), slug, '')
            itunes_categories = _get_with_default_key(
                config.get('POSTCAST_ITUNES_CATEGORIES', {}), slug, '')

            for lang in config['TRANSLATIONS']:
                if category:
                    title = config.get('CATEGORY_TITLES', {}).get(category)
                    description = config.get('CATEGORY_DESCRIPTIONS', {}).get(category)
                else:
                    title = None
                    description = None

                posts = [
                    post for post in self.site.posts
                    if post.is_translation_available(lang) and
                    (post.meta('category', lang) == category if category else True) and
                    (set(post.tags_for_language(lang)) >= set(tags) if tags else True)
                ]

                feed_deps = [self.site.configuration_filename]
                for post in posts:
                    feed_deps.append(post.source_path)
                    audio_path = self.audio_path(lang=lang, post=post)
                    if audio_path:
                        feed_deps.append(audio_path)

                output_path = self.feed_path(slug, lang)

                yield {
                    'basename': self.name,
                    'name': str(output_path),
                    'targets': [output_path],
                    'file_dep': feed_deps,
                    'clean': True,
                    'actions': [(self.render_feed, [slug, posts, output_path], {
                        'description': description,
                        'itunes_categories': itunes_categories,
                        'itunes_explicit': itunes_explicit,
                        'itunes_image': itunes_image,
                        'lang': lang,
                        'title': title,
                    })]
                }

    def render_feed(self, slug, posts, output_path, lang=None, title=None, description=None, itunes_explicit=None, itunes_categories=None, itunes_image=None):
        config = self.site.config
        rss_obj = self.site.generic_rss_feed(
            lang=lang,
            title=title,
            link=config['SITE_URL'],
            description=description,
            timeline=posts,
            rss_teasers=True,
            rss_plain=True,
            feed_length=config['FEED_LENGTH'],
            feed_url=self.feed_url(slug, lang),
            enclosure=self.enclosure,
        )
        rss_obj = self.with_itunes_tags(
            rss_obj, lang, posts,
            explicit=itunes_explicit,
            image=itunes_image,
            categories=itunes_categories,
        )
        utils.rss_writer(rss_obj, output_path)
        return output_path

    def with_itunes_tags(self, rss_obj, lang, posts, explicit=None, image=None, categories=None):
        config = self.site.config
        rss_obj = ITunesRSS2.from_rss2(rss_obj)
        rss_obj.rss_attrs["xmlns:itunes"] = "http://www.itunes.com/dtds/podcast-1.0.dtd"
        rss_obj.itunes_author = config['BLOG_AUTHOR'](lang)
        rss_obj.itunes_name = config['BLOG_AUTHOR'](lang)
        rss_obj.itunes_email = config['BLOG_EMAIL']
        rss_obj.itunes_summary = rss_obj.description
        rss_obj.itunes_explicit = explicit
        if image:
            rss_obj.itunes_image = urljoin(config['BASE_URL'], image)
        rss_obj.itunes_categories = categories

        itunes_items = []
        for post, item in zip(posts, rss_obj.items):
            itunes_item = ITunesItem.from_rss_item(item)
            for suffix in ('subtitle', 'duration', 'explicit'):
                tag = 'itunes_{}'.format(suffix)
                setattr(itunes_item, tag, post.meta(tag, lang))
            itunes_item.itunes_author = post.meta('itunes_author', lang) or post.author(lang)
            itunes_item.itunes_summary = post.meta('itunes_summary', lang) or itunes_item.description
            if post.meta('itunes_image', lang):
                itunes_item.itunes_image = self.site.url_replacer(
                    post.permalink(), post.meta('itunes_image', lang), lang, 'absolute')
            itunes_items.append(itunes_item)
        rss_obj.items = itunes_items

        return rss_obj

    def feed_url(self, slug, lang=None):
        config = self.site.config
        return urljoin(config['BASE_URL'], self.feed_path(slug, lang=lang, is_link=True))

    def feed_path(self, slug, lang=None, is_link=False):
        config = self.site.config
        path = []
        if not is_link:
            path.append(config['OUTPUT_FOLDER'])
        path.append(config.get('POSTCAST_PATH', 'casts'))
        path.extend([config['TRANSLATIONS'][lang], '{}.xml'.format(slug)])
        return os.path.normpath(os.path.join(*path))

    def enclosure(self, post=None, lang=None):
        download_url = self.audio_url(lang=lang, post=post)
        audio_path = self.audio_path(lang=lang, post=post)
        if audio_path:
            download_size = os.stat(audio_path).st_size
        else:
            try:
                download_size = int(requests.head(download_url, allow_redirects=True).headers['content-length'])
            except requests.RequestException:
                return None
        download_type, _ = mimetypes.guess_type(download_url)
        if not download_type:
            return None
        return download_url, download_size, download_type

    def audio_url(self, lang=None, post=None):
        config = self.site.config
        if urlparse(post.meta('enclosure', lang)).scheme:
            return post.meta('enclosure', lang)
        else:
            base_url = config.get('POSTCAST_BASE_URL', config['BASE_URL'])
            return urljoin(base_url, self.audio_path(lang=lang, post=post, is_link=True))

    def audio_path(self, lang=None, post=None, is_link=False):
        if urlparse(post.meta('enclosure', lang)).scheme or not post:
            return None

        config = self.site.config
        enclosure_path = config.get('POSTCAST_ENCLOSURE_FOLDER')
        path = []
        if not is_link:
            if enclosure_path:
                path.append(enclosure_path)
            else:
                path.append(config['OUTPUT_FOLDER'])
        if not enclosure_path:
            path.append(os.path.dirname(post.destination_path(lang=lang)))
        path.append(post.meta('enclosure', lang))
        return os.path.normpath(os.path.join(*path))


class ITunesRSS2(utils.ExtendedRSS2):
    """Extended RSS class."""

    xsl_stylesheet_href = None

    def __init__(self, itunes_author=None, itunes_summary=None,
                 itunes_name=None, itunes_email=None,
                 itunes_image=None, itunes_categories=None,
                 itunes_explicit=None, **kwargs):
        utils.ExtendedRSS2.__init__(self, **kwargs)
        self.itunes_author = itunes_author
        self.itunes_summary = itunes_summary
        self.itunes_name = itunes_name
        self.itunes_email = itunes_email
        self.itunes_image = itunes_image
        self.itunes_categories = itunes_categories
        self.itunes_explicit = itunes_explicit

    @classmethod
    def from_rss2(cls, rss2):
        new_rss2 = cls(title=rss2.title, link=rss2.link,
                       description=rss2.description)
        new_rss2.__dict__.update(rss2.__dict__)
        return new_rss2

    def publish_extensions(self, handler):
        utils.ExtendedRSS2.publish_extensions(self, handler)

        for tag in ('author', 'summary'):
            _simple_itunes_tag(self, handler, tag)
        _itunes_image_tag(self, handler)
        _itunes_explicit_tag(self, handler)

        if self.itunes_name or self.itunes_email:
            handler.startElement("itunes:owner", {})
            _simple_itunes_tag(self, handler, 'name')
            _simple_itunes_tag(self, handler, 'email')
            handler.endElement("itunes:owner")

        if self.itunes_categories:
            for category_entry in self.itunes_categories:
                try:
                    category, subcategories = category_entry
                except ValueError:
                    category = category_entry[0]
                    subcategories = ()
                handler.startElement("itunes:category", {'text': category})
                for subcategory in subcategories:
                    handler.startElement("itunes:category", {'text': subcategory})
                    handler.endElement("itunes:category")
                handler.endElement("itunes:category")

    def _itunes_attributes(self):
        for tag in ('author', 'summary', 'name', 'email', 'image', 'categories', 'explicit'):
            yield 'itunes:{}'.format(tag), getattr(self, 'itunes_{}'.format(tag))


class ITunesItem(utils.ExtendedItem):

    def __init__(self, itunes_author=None, itunes_subtitle=None,
                 itunes_summary=None, itunes_image=None,
                 itunes_duration=None, itunes_explicit=None, **kwargs):
        utils.ExtendedItem.__init__(self, **kwargs)
        self.itunes_author = itunes_author
        self.itunes_subtitle = itunes_subtitle
        self.itunes_summary = itunes_summary
        self.itunes_image = itunes_image
        self.itunes_duration = itunes_duration
        self.itunes_explicit = itunes_explicit

    @classmethod
    def from_rss_item(cls, item):
        new_item = cls(title=item.title, link=item.link, description=item.description)
        new_item.__dict__.update(item.__dict__)
        return new_item

    def publish_extensions(self, handler):
        utils.ExtendedItem.publish_extensions(self, handler)
        for tag in ('author', 'subtitle', 'summary', 'duration'):
            _simple_itunes_tag(self, handler, tag)
        _itunes_image_tag(self, handler)
        _itunes_explicit_tag(self, handler)


def _simple_itunes_tag(src, handler, tag):
    itunes_tag = "itunes:{}".format(tag)
    value = getattr(src, 'itunes_{}'.format(tag))
    if value:
        handler.startElement(itunes_tag, {})
        handler.characters(value)
        handler.endElement(itunes_tag)


def _itunes_explicit_tag(src, handler):
    if src.itunes_explicit is not None:
        handler.startElement("itunes:explicit", {})
        handler.characters("yes" if src.itunes_explicit else "no")
        handler.endElement("itunes:explicit")


def _itunes_image_tag(src, handler):
    if src.itunes_image:
        handler.startElement("itunes:image", {'href': src.itunes_image})
        handler.endElement("itunes:image")


def _get_with_default_key(config, key, default_key):
    return config.get(key, config.get(default_key))
