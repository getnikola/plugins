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

    name = "link_figure"

    def set_site(self, site):
        self.site = site
        directives.register_directive('link_figure', LinkFigure)
        return super(Plugin, self).set_site(site)

CODE_URL_BASIC = (u"""<a class="{classes}"
href="{url}"
title="{description}">
{title}
</a>""")

CODE_IMAGE = (u"""<div class="link-figure-media">
<a class="link-figure-image" href="{url}" target="_blank">
<img src="{image_url}" alt="{title}" />
</a>
</div>""")

CODE_DESCRIPTION = (u"""<p class="link-figure-description">
{description}
</p>""")

CODE_AUTHOR = (u"""<p class="link-figure-author">
@ {author}
</p>""")

CODE_AUTHOR_URL = (u"""<p class="link-figure-author">
@ <a href="{author_url}" target="_blank">
{author}
</a></p>""")

CODE_URL = (u"""<div class="link-figure-content">
<a class="link-figure-title" href="{url}" target="_blank">{title}</a>
{description}
{author}
</div>""")

CODE = (u"""<div class="{classes}">
{image_url}
{url}
</div>""")


class LinkFigure(Directive):
    """ Restructured text extension for inserting link figure

        Usage:

            .. link_figure:: url
                :title: url title
                :description: url description
                :class: class name
                :image_url: url image
                :author: url domain or author
                :author_url: author url
   """

    has_content = False
    required_arguments = 1
    optional_arguments = 6
    option_spec = {
        'title': directives.unchanged,
        'description': directives.unchanged,
        'class': directives.unchanged,
        'image_url': directives.unchanged,
        'author': directives.unchanged,
        'author_url': directives.unchanged,
    }

    def run(self):
        """ Required by the Directive interface. Create docutils nodes """
        options = {
            'url': self.arguments[0],
            'title': self.options.get('title', ''),
            'description': self.options.get('description', ''),
            'classes': self.options.get('class', ''),
            'image_url': self.options.get('image_url', ''),
            'author': self.options.get('author', ''),
            'author_url': self.options.get('author_url', ''),
        }
        if not options['title']:
            if options['url'].endswith('/'):
                options['title'] = options['url'][:-1]
            options['title'] = options['title'].split('/')[-1]
            options['title'] = options['title'].split('?')[0]
            if not options['description']:
                options['description'] = options['title']
            return [nodes.raw('', CODE_URL_BASIC.format(**options), format='html')]
        if options['image_url']:
            options['image_url'] = CODE_IMAGE.format(**options)
        if options['author'] and options['author_url']:
            options['author'] = CODE_AUTHOR_URL.format(**options)
        elif options['author']:
            options['author'] = CODE_AUTHOR.format(**options)
        if options['description']:
            options['description'] = CODE_DESCRIPTION.format(**options)
        options['url'] = CODE_URL.format(**options)
        return [nodes.raw('', CODE.format(**options), format='html')]

    def assert_has_content(self):
        """ LinkFigure has no content, override check from superclass """
        pass
