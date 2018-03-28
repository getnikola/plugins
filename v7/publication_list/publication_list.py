# -*- coding: utf-8 -*-

# Copyright © 2016-2017 Hong Xu <hong@topbug.net>.

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

import os
import sys

from docutils import nodes
from docutils.parsers.rst import Directive, directives

from nikola.plugin_categories import RestExtension

from pybtex.database import BibliographyData, Entry
from pybtex.database.input.bibtex import Parser
from pybtex.markup import LaTeXParser
from pybtex.style.formatting.unsrt import Style as UnsrtStyle
from pybtex.style.template import href, tag


class Style(UnsrtStyle):
    """The style for publication listing. It hyperlinks the title to the detail page if user sets it.
    """

    def __init__(self, detail_page_url):
        super().__init__()
        self.detail_page_url = detail_page_url

    def format_title(self, e, which_field, as_sentence=True):
        "Override the UnsrtStyle format_title(), so we have the title hyperlinked."

        title = tag('strong')[super().format_title(e, which_field, as_sentence)]

        if self.detail_page_url:
            url = '/'.join((self.detail_page_url, e.label + '.html'))
            return href[url, title]
        else:
            return title


class Plugin(RestExtension):

    name = "publication_list"

    def set_site(self, site):
        self.site = site
        directives.register_directive('publication_list', PublicationList)
        PublicationList.site = self.site
        PublicationList.output_folder = self.site.config['OUTPUT_FOLDER']
        return super(Plugin, self).set_site(site)


class PublicationList(Directive):
    """
    Directive to list publications.
    """
    has_content = False
    required_arguments = 1
    optional_arguments = sys.maxsize
    option_spec = {
        'bibtex_dir': directives.unchanged,
        'detail_page_dir': directives.unchanged,
        'highlight_author': directives.unchanged,
        'style': directives.unchanged
    }

    def run(self):

        bibtex_dir = self.options.get('bibtex_dir', 'bibtex')
        detail_page_dir = self.options.get('detail_page_dir', 'papers')
        highlight_authors = self.options.get('highlight_author', None)
        if highlight_authors:
            highlight_authors = highlight_authors.split(';')
        style = Style(self.site.config['BASE_URL'] + detail_page_dir if detail_page_dir else None)
        self.state.document.settings.record_dependencies.add(self.arguments[0])

        parser = Parser()

        all_entries = []
        for a in self.arguments:
            all_entries.extend(parser.parse_file(a).entries.items())
        # Sort the publication entries by year reversed
        data = sorted(all_entries, key=lambda e: e[1].fields['year'], reverse=True)

        html = '<div class="publication-list">\n'
        cur_year = None

        if bibtex_dir:  # create the bibtex dir if the option is set
            try:
                os.makedirs(os.path.sep.join((self.output_folder, bibtex_dir)))
            except OSError:  # probably because the dir already exists
                pass

        if detail_page_dir:  # create the detail page dir if the option is set
            try:
                os.makedirs(os.path.sep.join((self.output_folder, detail_page_dir)))
            except OSError:  # probably because the dir already exists
                pass

        for label, entry in data:
            # print a year title when year changes
            if entry.fields['year'] != cur_year:
                if cur_year is not None:  # not first year group
                    html += '</ul>'
                cur_year = entry.fields['year']
                html += '<h3>{}</h3>\n<ul>'.format(cur_year)

            entry.label = label  # Pass label to the style.
            pub_html = list(style.format_entries((entry,)))[0].text.render_as('html')
            if highlight_authors:  # highlight one of several authors (usually oneself)
                for highlight_author in highlight_authors:
                    # We need to replace all occurrence of space except for the last one with
                    # &nbsp;, since pybtex does it for all authors
                    count = highlight_author.count(' ') - 1
                    pub_html = pub_html.replace(
                        highlight_author.strip().replace(' ', '&nbsp;', count),
                        '<strong>{}</strong>'.format(highlight_author), 1)
            html += '<li class="publication" style="padding-bottom: 1em;">' + pub_html

            extra_links = ""

            if 'fulltext' in entry.fields:  # the link to the full text, usually a link to the pdf file
                extra_links += '[<a href="{}">full text</a>] '.format(entry.fields['fulltext'])

            bibtex_fields = dict(entry.fields)
            # Collect and remove custom links (fields starting with "customlink")
            custom_links = dict()
            for key, value in bibtex_fields.items():
                if key.startswith('customlink'):
                    custom_links[key[len('customlink'):]] = value
            # custom fields (custom links)
            for key, value in custom_links.items():
                extra_links += '[<a href="{}">{}</a>] '.format(value, key)

            # Remove some fields for the publicly available BibTeX file since they are mostly only
            # used by this plugin.
            for field_to_remove in ('abstract', 'fulltext'):
                if field_to_remove in bibtex_fields:
                    del bibtex_fields[field_to_remove]
            # Prepare for the bib file. Note detail_page_dir may need bib_data later.
            bibtex_entry = Entry(entry.type, bibtex_fields, entry.persons)
            bib_data = BibliographyData(dict({label: bibtex_entry}))
            bib_string = bib_data.to_string('bibtex')
            extra_links += '''
            [<a href="javascript:void(0)" onclick="
            (function(target, id) {{
              if ($('#' + id).css('display') == 'block')
              {{
                $('#' + id).hide('fast');
                $(target).text('BibTeX&#x25BC;')
              }}
              else
              {{
                $('#' + id).show('fast');
                $(target).text('BibTeX&#x25B2;')
              }}
            }})(this, '{}');">BibTeX&#x25BC;</a>]
            '''.format('bibtex-' + label)
            if bibtex_dir:  # write bib files to bibtex_dir for downloading
                bib_link = '{}/{}.bib'.format(bibtex_dir, label)
                bib_data.to_file('/'.join([self.output_folder, bib_link]), 'bibtex')

            if extra_links or detail_page_dir or 'abstract' in entry.fields:
                html += '<br>'

            # Add the abstract link.
            if 'abstract' in entry.fields:
                html += '''
                [<a href="javascript:void(0)" onclick="
                (function(target, id) {{
                  if ($('#' + id).css('display') == 'block')
                {{
                  $('#' + id).hide('fast');
                  $(target).text('abstract&#x25BC;')
                }}
                else
                {{
                  $('#' + id).show('fast');
                  $(target).text('abstract&#x25B2;')
                }}
                }})(this, '{}');">abstract&#x25BC;</a>] '''.format('abstract-' + label)

            display_none = '<div id="{}" style="display:none"><pre>{}</pre></div>'
            bibtex_display = display_none.format(
                'bibtex-' + label, bib_string)

            abstract_text = str(
                LaTeXParser(entry.fields['abstract']).parse()) if 'abstract' in entry.fields else ''
            if detail_page_dir:  # render the details page of a paper
                page_url = '/'.join((detail_page_dir, label + '.html'))
                html += '[<a href="{}">details</a>] '.format(
                    self.site.config['BASE_URL'] + page_url)
                context = {
                    'title': str(LaTeXParser(entry.fields['title']).parse()),
                    'abstract': abstract_text,
                    'bibtex': bib_data.to_string('bibtex'),
                    'bibtex_link': '/' + bib_link if bibtex_dir else '',
                    'default_lang': self.site.config['DEFAULT_LANG'],
                    'label': label,
                    'lang': self.site.config['DEFAULT_LANG'],
                    'permalink': self.site.config['SITE_URL'] + page_url,
                    'reference': pub_html,
                    'extra_links': extra_links + bibtex_display
                }

                if 'fulltext' in entry.fields:
                    context['pdf'] = entry.fields['fulltext']

                self.site.render_template(
                    'publication.tmpl',
                    os.path.sep.join((self.output_folder, detail_page_dir, label + '.html')),
                    context,
                )

            html += extra_links

            # Add the hidden abstract and bibtex.
            if 'abstract' in entry.fields:
                html += '''
                <div id="{}" class="publication-abstract" style="display:none">
                <blockquote>{}</blockquote></div>
                '''.format('abstract-' + label, abstract_text)
            html += bibtex_display
            html += '</li>'

        if len(data) != 0:  # publication list is nonempty
            html += '</ul>'

        html += '</div>'

        return [nodes.raw('', html, format='html'), ]
