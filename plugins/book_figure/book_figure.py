# -*- coding: utf-8 -*-

# Copyright © 2014 Ivan Teoh and others.

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

from docutils import nodes
from docutils.parsers.rst import Directive, directives

from nikola.plugin_categories import RestExtension


class Plugin(RestExtension):

    name = "book_figure"

    def set_site(self, site):
        self.site = site
        directives.register_directive('book_figure', BookFigure)
        return super(Plugin, self).set_site(site)

CODE_IMAGE = ("""<div class="book-figure-media">
<a class="book-figure-image" href="{url}" target="_blank">
<img src="{image_url}" alt="{title}" />
</a>
</div>""")

CODE_URL = ("""<a class="book-figure-title" href="{url}" target="_blank">{title}</a>""")

CODE_TITLE = ("""<p class="book-figure-title">{title}</p>""")

CODE_AUTHOR = ("""<p class="book-figure-author">
by {author}
</p>""")

CODE_ISBN_13 = ("""<tr>
<th>ISBN-13:</th>
<td>{isbn_13}</td>
</tr>""")

CODE_ISBN_10 = ("""<tr>
<th>ISBN-10:</th>
<td>{isbn_10}</td>
</tr>""")

CODE_ASIN = ("""<tr>
<th>ASIN:</th>
<td>{asin}</td>
</tr>""")

CODE_BOOK_NUMBER = ("""<table class="book-figure-book-number"><tbody>
{isbn_13}
{isbn_10}
{asin}
</tbody></table>""")

CODE_REVIEW = ("""<div class="book-figure-review">
{review}
</div>""")

CODE_BOOK = ("""<div class="book-figure-content">
{url}
{author}
{book_number}
{review}
</div>""")

CODE = ("""<div class="{classes}">
{image_url}
{title}
</div>""")


class BookFigure(Directive):
    """ Restructured text extension for inserting book figure

        Usage:

        .. book_figure:: title
            :class: class name
            :url: book url
            :author: book author
            :isbn_13: ISBN13
            :isbn_10: ISBN10
            :asin: ASIN
            :image_url: book cover image url

            Your review.
   """

    has_content = True
    required_arguments = 1
    optional_arguments = 7
    option_spec = {
        'class': directives.unchanged,
        'url': directives.unchanged,
        'author': directives.unchanged,
        'isbn_13': directives.unchanged,
        'isbn_10': directives.unchanged,
        'asin': directives.unchanged,
        'image_url': directives.unchanged,
    }

    def run(self):
        """ Required by the Directive interface. Create docutils nodes """
        options = {
            'title': self.arguments[0],
            'classes': self.options.get('class', ''),
            'url': self.options.get('url', ''),
            'author': self.options.get('author', ''),
            'isbn_13': self.options.get('isbn_13', ''),
            'isbn_10': self.options.get('isbn_10', ''),
            'asin': self.options.get('asin', ''),
            'image_url': self.options.get('image_url', ''),
        }
        if options['image_url']:
            options['image_url'] = CODE_IMAGE.format(**options)
        if options['author']:
            options['author'] = CODE_AUTHOR.format(**options)
        if options['isbn_13']:
            options['isbn_13'] = CODE_ISBN_13.format(**options)
        if options['isbn_10']:
            options['isbn_10'] = CODE_ISBN_10.format(**options)
        if options['asin']:
            options['asin'] = CODE_ASIN.format(**options)
        options['book_number'] = ''
        if options['isbn_13'] or options['isbn_10'] or options['asin']:
            options['book_number'] = CODE_BOOK_NUMBER.format(**options)
        options['review'] = ''
        for line in self.content:
            options['review'] += '<p>{0}</p>'.format(line)
        if options['review']:
            options['review'] = CODE_REVIEW.format(**options)
        if options['url']:
            options['url'] = CODE_URL.format(**options)
        else:
            options['url'] = CODE_TITLE.format(**options)
        options['title'] = CODE_BOOK.format(**options)
        return [nodes.raw('', CODE.format(**options), format='html')]
