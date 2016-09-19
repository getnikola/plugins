# -*- coding: utf-8 -*-

# Copyright © 2016 Hong Xu <hong@topbug.net>.

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

from docutils import nodes
from docutils.parsers.rst import Directive, directives

from nikola.plugin_categories import RestExtension

from pybtex.database import BibliographyData, Entry
from pybtex.database.input.bibtex import Parser
from pybtex.plugin import find_plugin


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
    option_spec = {
        'bibtex_dir': directives.unchanged,
        'detail_page_dir': directives.unchanged,
        'highlight_author': directives.unchanged,
        'style': directives.unchanged
    }

    def run(self):

        style = find_plugin('pybtex.style.formatting', self.options.get('style', 'unsrt'))()
        bibtex_dir = self.options.get('bibtex_dir', 'bibtex')
        detail_page_dir = self.options.get('detail_page_dir', 'papers')
        highlight_author = self.options.get('highlight_author', None)
        self.state.document.settings.record_dependencies.add(self.arguments[0])

        parser = Parser()

        # Sort the publication entries by year reversed
        data = sorted(parser.parse_file(self.arguments[0]).entries.items(),
                      key=lambda e: e[1].fields['year'], reverse=True)

        html = '<div class="publication-list">\n'
        cur_year = None

        if bibtex_dir:  # create the bibtex dir if the option is set
            try:
                os.mkdir(os.path.sep.join((self.output_folder, bibtex_dir)))
            except OSError:  # probably because the dir already exists
                pass

        if detail_page_dir:  # create the detail page dir if the option is set
            try:
                os.mkdir(os.path.sep.join((self.output_folder, detail_page_dir)))
            except OSError:  # probably because the dir already exists
                pass

        for label, entry in data:
            # print a year title when year changes
            if entry.fields['year'] != cur_year:
                if cur_year is not None:  # not first year group
                    html += '</ul>'
                cur_year = entry.fields['year']
                html += '<h3>{}</h3>\n<ul>'.format(cur_year)

            pub_html = list(style.format_entries((entry,)))[0].text.render_as('html')
            if highlight_author:  # highlight an author (usually oneself)
                pub_html = pub_html.replace(highlight_author,
                                            '<strong>{}</strong>'.format(highlight_author), 1)
            html += '<li class="publication">' + pub_html

            extra_links = ""
            bibtex_fields = dict(entry.fields)
            # Remove some fields for the publicly available BibTeX file since they are mostly only
            # used by this plugin.
            for field_to_remove in ('abstract', 'fulltext'):
                if field_to_remove in bibtex_fields:
                    del bibtex_fields[field_to_remove]
            bibtex_entry = Entry(entry.type, bibtex_fields, entry.persons)
            # detail_page_dir may need bib_data later
            bib_data = BibliographyData(dict({label: bibtex_entry}))
            if bibtex_dir:  # write bib files to bibtex_dir for downloading
                bib_link = '{}/{}.bib'.format(bibtex_dir, label)
                bib_data.to_file('/'.join([self.output_folder, bib_link]), 'bibtex')
                extra_links += '[<a href="{}">BibTeX</a>] '.format(
                    self.site.config['BASE_URL'] + bib_link)

            if 'fulltext' in entry.fields:  # the link to the full text, usually a link to the pdf file
                extra_links += '[<a href="{}">full text</a>] '.format(entry.fields['fulltext'])

            if extra_links or detail_page_dir:
                html += '<br>'
            html += extra_links

            if detail_page_dir:  # render the details page of a paper
                page_url = '/'.join((detail_page_dir, label + '.html'))
                html += ' [<a href="{}">abstract and details</a>]'.format(
                    self.site.config['BASE_URL'] + page_url)
                context = {
                    'title': entry.fields['title'],
                    'abstract': entry.fields['abstract'] if 'abstract' in entry.fields else '',
                    'bibtex': bib_data.to_string('bibtex'),
                    'bibtex_link': '/' + bib_link if bibtex_dir else '',
                    'default_lang': self.site.config['DEFAULT_LANG'],
                    'label': label,
                    'lang': self.site.config['DEFAULT_LANG'],
                    'permalink': self.site.config['SITE_URL'] + page_url,
                    'reference': pub_html,
                    'extra_links': extra_links
                }

                if 'fulltext' in entry.fields and entry.fields['fulltext'].endswith('.pdf'):
                    context['pdf'] = entry.fields['fulltext']

                self.site.render_template(
                    'publication.tmpl',
                    os.path.sep.join((self.output_folder, detail_page_dir, label + '.html')),
                    context,
                )

            html += '</li>'

        if len(data) != 0:  # publication list is nonempty
            html += '</ul>'

        html += '</div>'

        return [nodes.raw('', html, format='html'), ]
