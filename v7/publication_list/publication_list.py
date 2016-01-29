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

from pybtex.database import BibliographyData
from pybtex.database.input.bibtex import Parser
from pybtex.plugin import find_plugin


class Plugin(RestExtension):

    name = "publication_list"

    def set_site(self, site):
        self.site = site
        directives.register_directive('publication_list', PublicationList)
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
        'style': directives.unchanged
    }

    def run(self):

        style = find_plugin('pybtex.style.formatting', self.options.get('style', 'unsrt'))()
        bibtex_dir = self.options.get('bibtex_dir', 'bibtex')

        parser = Parser()

        # Sort the publication entries by year reversed
        data = sorted(parser.parse_file(self.arguments[0]).entries.items(),
                      key=lambda e: e[1].fields['year'], reverse=True)

        print(type(data))
        html = '<div class = "publication-list">\n'
        cur_year = None

        if bibtex_dir:  # create the bibtex dir if the option is set
            try:
                os.mkdir(os.path.sep.join((self.output_folder, bibtex_dir)))
            except OSError:  # probably because the dir already exists
                pass

        for label, entry in data:
            # print a year title when year changes
            if entry.fields['year'] != cur_year:
                if cur_year is not None:  # not first year group
                    html += '</ul>'
                cur_year = entry.fields['year']
                html += '<h3>{}</h3>\n<ul>'.format(cur_year)

            html += '<li class = "publication">{}'.format(
                list(style.format_entries((entry,)))[0].text.render_as('html'))

            extra_links = ""
            if bibtex_dir:  # write bib files to bibtex_dir for downloading
                bib_link = '{}/{}.bib'.format(bibtex_dir, label)
                bib_data = BibliographyData(dict({label: entry}))
                bib_data.to_file('/'.join([self.output_folder, bib_link]), 'bibtex')
                extra_links += '[<a href="{}">bibtex</a>] '.format(bib_link)

            if 'pdf' in entry.fields:  # the link to the pdf file
                extra_links += '[<a href="{}">pdf</a>] '.format(entry.fields['pdf'])

            if extra_links:
                html += '<br/>' + extra_links

            html += '</li>'

        if len(data) != 0:  # publication list is nonempty
            html += '</ul>'

        html += '</div>'

        return [nodes.raw('', html, format='html'), ]
