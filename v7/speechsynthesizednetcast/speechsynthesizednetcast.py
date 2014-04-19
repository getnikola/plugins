# -*- coding: utf-8 -*-

# Copyright © 2013–2014 Daniel Aleksandersen and others.

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

from __future__ import print_function
import codecs
from datetime import datetime
import os
import sys
import time
import tempfile
import shutil
try:
    from urlparse import urljoin
except ImportError:
    from urllib.parse import urljoin  # NOQA

from nikola.plugin_categories import Task

from nikola import utils

class SpeechSynthesizedNetcast(Task):
    """Archive site updates."""
    name = "speechsynthesizednetcast"

    doc_purpose = "Save new posts in the Internet Archives"

    is_default = True

    def set_site(self, site):
        site.register_path_handler('opus_feed_path', self.feed_opus_path)
        site.register_path_handler('vorbis_feed_path', self.feed_vorbis_path)
        site.register_path_handler('mpeg_feed_path', self.feed_mpeg_path)
        return super(SpeechSynthesizedNetcast, self).set_site(site)

    logger = None

    default_audio_formats = ["opus", "oga"]
    default_text_intro = "Hello. Now reading the blog post titled, {title}. By {author}. Published on {date}."
    default_text_outro = "Thank you for listening. The written version of this program is available at {permalink} . Where you might find additional visual content, reader commentary, and more."

    def gen_tasks(self):

        self.logger = utils.get_logger('speechsynthesizednetcast', self.site.loghandlers)

        # Deps and config
        kw = {
            "translations": self.site.config['TRANSLATIONS'],
            "blog_title": self.site.config['BLOG_TITLE'],
            "blog_description": self.site.config['BLOG_DESCRIPTION'],
            "site_url": self.site.config['SITE_URL'],
            "blog_description": self.site.config['BLOG_DESCRIPTION'],
            "output_folder": self.site.config['OUTPUT_FOLDER'],
            "cache_folder": self.site.config['CACHE_FOLDER'],
            "feed_length": self.site.config['FEED_LENGTH'],
            "default_lang" : self.site.config['DEFAULT_LANG'],
            "audio_formats" : self.default_audio_formats,
            "intro_text" : self.default_text_intro,
            "outro_text" : self.default_text_outro,
        }

        # Default configuration values
        if 'NETCAST_AUDIO_FORMATS' in self.site.config:
            kw['audio_formats'] = self.site.config['NETCAST_AUDIO_FORMATS']
        if 'NETCAST_INTRO' in self.site.config:
            kw['intro_text'] = self.site.config['NETCAST_INTRO']
        if 'NETCAST_OUTRO' in self.site.config:
            kw['outro_text'] = self.site.config['NETCAST_OUTRO']

        self.test_required_programs([kw['audio_formats']])

        self.site.scan_posts()
        yield self.group_task()

        for lang in kw['translations']:
            feed_deps = []
            posts = [x for x in self.site.posts if x.is_translation_available(lang)][:10]
            for post in posts:
                post_recording_path = self.netcast_audio_path(lang=lang, post=post, format='flac', is_cache=True)
                yield {'name': str(post_recording_path),
                    'basename': str(self.name),
                    'targets': [post_recording_path],
                    'file_dep': post.fragment_deps(lang),
                    'uptodate' : [utils.config_changed(kw)],
                    'clean': True,
                    'actions': [(self.record_post, [post_recording_path, post, lang])]
                }

                for format in kw['audio_formats']:
                    output_name = self.netcast_audio_path(lang=lang, post=post, format=format)
                    yield {'name': str(output_name),
                        'basename': str(self.name),
                        'targets': [output_name],
                        'file_dep': [post_recording_path],
                        'clean': True,
                        'actions': [(self.encode_post, [output_name, post_recording_path, post, lang, format])]
                    }
                    feed_deps.append(output_name)

            for format in kw['audio_formats']:
                output_name = self.netcast_feed_path(lang=lang, format=format)
                yield {'name': str(output_name),
                    'basename': str(self.name),
                    'targets': [output_name],
                    'file_dep': feed_deps,  # depends on all formats
                   'clean': True,
                   'actions': [(self.netcast_feed_renderer, [lang, posts, output_name, format])]
                }
    def test_required_programs(self, formats):
        # Test availability of required programs
        programs = ['espeak', 'flac', 'sox']
        if 'opus' in formats:
            programs.append('opusenc')
        if 'oga' in formats:
            programs.append('oggenc')
        if 'mp3' in formats:
            programs.append('lame')
        not_found = []
        for program in programs:
            found = False
            for path in os.environ['PATH'].split(os.pathsep):
                if os.access(os.path.join(path.strip('"'), program), os.X_OK):
                   found = True
            if not found:
                not_found.append(program)
        if not_found:
            utils.req_missing(not_found, 'create speech-synthesized netcasts', python=False, optional=False)

    def netcast_feed_link(self, lang=None, format=None):
        return urljoin(self.site.config['BASE_URL'], self.netcast_feed_path(lang=lang, format=format, is_link=True))

    def netcast_feed_path(self, lang=None, format=None, is_link=False):
        path = []
        if not is_link:
            path.append(self.site.config['OUTPUT_FOLDER'])
        path.extend([self.site.config['TRANSLATIONS'][lang], 'netcast.{0}.rss'.format(format)])

        return os.path.normpath(os.path.join(*path))

    def netcast_feed_renderer(self, lang=None, posts=None, output_path=None, format=None):
        utils.generic_rss_renderer(lang=lang,
                                   title="{0} netcast ({1})".format(self.site.config['BLOG_TITLE'](lang), format.upper()),
                                   link=self.site.config['SITE_URL'],
                                   description=self.site.config['BLOG_DESCRIPTION'](lang),
                                   timeline=posts,
                                   output_path=output_path,
                                   rss_teasers=True,
                                   rss_plain=False,
                                   feed_length=self.site.config['FEED_LENGTH'],
                                   feed_url=self.netcast_feed_link(lang=lang, format=format),
                                   enclosure=self.enclosure_tuple_format(format, self.enclosure_tuple)
        )
        return output_path

    def enclosure_tuple_format(self, format, routine):
        def new_routine(*args, **kw):
            return routine(format=format, *args, **kw)
        return new_routine

    # Called from generic_rss_renderer(enclosure=callback)
    def enclosure_tuple(self, post=None, lang=None, format=None):
        download_link = self.netcast_audio_link(lang=lang, post=post, format=format)
        download_size = os.stat(self.netcast_audio_path(lang=lang, post=post, format=format)).st_size
        # because mimetypes.guess_type() blows
        filetypes = {'opus': 'audio/opus', 'oga': 'audio/ogg', 'mp3': 'audio/mpeg'}
        try:
            download_type = filetypes[format]
        except KeyError:
            return False

        return download_link, download_size, download_type

    def netcast_audio_link(self, lang=None, post=None, format=None):
        return urljoin(self.site.config['BASE_URL'], self.netcast_audio_path(lang=lang, post=post, format=format, is_link=True))

    def netcast_audio_path(self, lang=None, post=None, format=None, is_link=False, is_cache=False):
        path = []
        if is_cache:
            path.append(self.site.config['CACHE_FOLDER'])
        elif not is_link:
            path.append(self.site.config['OUTPUT_FOLDER'])
        path.append(post.destination_path(lang=lang, extension='.'+format, sep=os.sep))

        return os.path.normpath(os.path.join(*path))

    def record_post(self, output_path, post, lang):
        workdir = tempfile.mkdtemp()
        utils.makedirs(os.path.dirname(output_path))

        # Intro text
        introfile = os.path.join(workdir, 'intro.wav')
        if 'NETCAST_INTRO' in self.site.config:
            introtext = self.site.config['NETCAST_INTRO'][lang].format(title=post.title(lang=lang),
                                                                       author=post.author(lang=lang),
                                                                       date=post.formatted_date("%A, %d. %B %Y"),
                                                                       permalink=self.site.abs_link(post.permalink()).split('//', 1)[1])
        else:
            introtext = self.default_text_intro.format(title=post.title(lang=lang),
                                                       author=post.author(lang=lang),
                                                       date=post.formatted_date("%A, %d. %B %Y"),
                                                       permalink=self.site.abs_link(post.permalink()).split('//', 1)[1])
        self.record_wave(lang, introfile, introtext, False, False)

        # Post text
        postfile = os.path.join(workdir, 'text.wav')
        posttextfile = os.path.join(workdir, 'text.txt')
        with codecs.open(posttextfile, 'wb+', 'utf8') as outf:
            outf.write(post.text(lang=lang, teaser_only=False, strip_html=False, show_read_more_link=False))
        self.record_wave(lang, postfile, False, posttextfile, False)

        # Outro
        outrofile = os.path.join(workdir, 'outro.wav')
        if 'NETCAST_OUTRO' in self.site.config:
            outrotext = self.site.config['NETCAST_OUTRO'][lang].format(title=post.title(lang=lang),
                                                                       author=post.author(lang=lang),
                                                                       date=post.formatted_date("%A, %d. %B %Y"),
                                                                       permalink=self.site.abs_link(post.permalink()).split('//', 1)[1])
        else:
            outrotext = self.default_text_outro.format(title=post.title(lang=lang),
                                                       author=post.author(lang=lang),
                                                       date=post.formatted_date("%A, %d. %B %Y"),
                                                       permalink=self.site.abs_link(post.permalink()).split('//', 1)[1])
        self.record_wave(lang, outrofile, outrotext, False, True)

        # Combined recording
        command = "sox {0} -p pad 0 0.8 | sox - {1} -p pad 0 0.8 | sox - {2} -p pad 0 1.2 | sox - -C 0 {3}".format(introfile, postfile, outrofile, output_path)
        os.system(command)

        shutil.rmtree(workdir)  # cleanup the tempdir

        return output_path

    def record_wave(self, lang, output_path, text, textfile, read_hyphen):
        command = "espeak -v {0} -m -b 1 -w {1} ".format(lang, output_path)
        if read_hyphen:  # for URLs
            command += ' --punct="-"'
        if textfile:
            command += ' -f {0}'.format(textfile)
        elif text:
            command += ' "{0}"'.format(text)
        os.system(command)

    def encode_post(self, output_name, post_recording, post, lang, format):
        utils.makedirs(os.path.dirname(output_name))
        if format == 'opus':
            self.encode_opus(post, lang, post_recording, output_name)
        elif format == 'oga':
            self.encode_vorbis(post, lang, post_recording, output_name)
        elif format == 'mp3':
            self.encode_mpeg(post, lang, post_recording, output_name)
        else:
            return False

        return output_name

    def encode_opus(self, post, lang, flac_path, output_path):
        command = 'opusenc --quiet --bitrate 30 --discard-comments --date "{0}" --genre "Vocal" --artist "{1}" --title "{2}" {3} {4}'.format(post.formatted_date("%Y-%m-%d"), post.author(lang=lang), post.title(lang=lang), flac_path, output_path)
        os.system(command)

    def encode_vorbis(self, post, lang, flac_path, output_path):
        command = 'oggenc --quiet --bitrate=30 --discard-comments --date "{0}" --genre "Vocal" --artist "{1}" --title "{2}" --output {3} {4}'.format(post.formatted_date("%Y-%m-%d"), post.author(lang=lang), post.title(lang=lang), output_path, flac_path)
        os.system(command)

    def encode_mpeg(self, post, lang, flac_path, output_path):
        command = 'flac --silent --decode --stdout {0} | lame --quiet --preset 32 --ignore-tag-errors --ty {1} --tg 28 --ta "{2}" --tt "{3}" - {4}'.format(flac_path, post.formatted_date("%Y"), post.author(lang=lang), post.title(lang=lang), output_path)
        os.system(command)

    def feed_opus_path(self, name, lang):
        return [_f for _f in [self.netcast_feed_path(self, lang=lang, format='opus')] if _f]

    def feed_vorbis_path(self, name, lang):
        return [_f for _f in [self.netcast_feed_path(self, lang=lang, format='oga')] if _f]

    def feed_mpeg_path(self, name, lang):
        return [_f for _f in [self.netcast_feed_path(self, lang=lang, format='mp3')] if _f]
