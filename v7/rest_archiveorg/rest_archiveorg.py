# -*- coding: utf-8 -*-
"""ReST directive to embed video and audio files from archive.org."""

from docutils import nodes
from docutils.parsers.rst import Directive, directives

from nikola.plugin_categories import RestExtension


TMPL_IFRAME = """\
<iframe class="archiveorg-player"
  src="https://archive.org/embed/{slug}{params}"
  width="{width}" height="{height}" frameborder="0"
  allowfullscreen webkitallowfullscreen="true" mozallowfullscreen="true" />
"""

TMPL_DOWNLOAD= """\
<p class="archiveorg-download-links"><span class="archiveorg-download-label"
>{download_label}</span>
<a href="https://archive.org/download/{slug}/{mp3}">MP3</a> |
<a href="https://archive.org/download/{slug}/{ogg}">Ogg Vorbis</a></p>
"""


class Plugin(RestExtension):
    """Plugin for archiveorg directive."""

    name = "rest_archiveorg"

    def set_site(self, site):
        """Set Nikola site."""
        self.site = site
        directives.register_directive('archiveorg', ArchiveOrg)
        return super(Plugin, self).set_site(site)


class ArchiveOrg(Directive):
    """ReST directive to embed video and audio files from archive.org."""

    has_content = False
    required_arguments = 1
    option_spec = {
        'autoplay': directives.flag,
        'download': directives.unchanged,
        'download_label': directives.unchanged,
        'height': directives.positive_int,
        'list_height': directives.positive_int,
        'playlist': directives.flag,
        'poster': directives.uri,
        'width': directives.positive_int,
    }

    def run(self):
        """Run the soundcloud directive."""
        options = {
            'slug': self.arguments[0],
            'width': 640,
            'height': 580 if 'playlist' in self.options else 45,
            'download_label': 'Download:',
            'params': []
        }
        options.update(self.options)

        if "autoplay" in options:
            options['params'].append('autoplay=1')

        if "playlist" in options:
            options['params'].append('playlist=1')

        if "list_height" in options:
            options['params'].append('list_height=%i' % options['list_height'])

        if "poster" in options:
            options['params'].append('poster=%s' % options['poster'])

        if options['params']:
            options['params'] = '?' + '&'.join(options['params'])
        else:
            options['params'] = ''

        elems = [nodes.raw('', TMPL_IFRAME.format(**options), format='html')]

        if "download" in options:
            options['mp3'] = options['download'] + '.mp3'
            options['ogg'] = options['download'] + '.ogg'
            elems.append(nodes.raw('', TMPL_DOWNLOAD.format(**options),
                                   format='html'))

        return elems


__all__ = ('ArchiveOrg', 'Plugin')
