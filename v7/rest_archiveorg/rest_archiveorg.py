# -*- coding: utf-8 -*-
"""ReST directive to embed video and audio files from archive.org."""

from docutils import nodes
from docutils.parsers.rst import Directive, directives

from nikola.plugin_categories import RestExtension

from archiveorg.provider import ArchiveOrgProvider


TMPL_DOWNLOAD= """\
<p class="archiveorg-download-links"><span class="archiveorg-download-label"
>{download_label}</span>
<a href="{mp3_url}">MP3</a> |
<a href="{ogg_url}">Ogg Vorbis</a></p>
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
        """Run the archiveorg directive."""
        identifier = self.arguments[0]
        opts = self.options
        pr = ArchiveOrgProvider()
        html = pr.get_player_iframe(identifier, opts)
        elems = [nodes.raw('', html, format='html')]

        if "download" in opts:
            opts.setdefault('download_label', 'Download:')
            opts['mp3_url'] = pr.get_download_url(identifier,
                                                  opts['download'] + '.mp3')
            opts['ogg_url'] = pr.get_download_url(identifier,
                                                  opts['download'] + '.ogg')
            elems.append(nodes.raw('', TMPL_DOWNLOAD.format(**opts),
                                   format='html'))

        return elems


__all__ = ('ArchiveOrg', 'Plugin')
