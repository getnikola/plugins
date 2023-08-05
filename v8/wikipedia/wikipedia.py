# -*- coding: utf-8 -*-

# Copyright © 2023 Lorenzo Rovigatti.

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

from nikola.plugin_categories import ShortcodePlugin
from nikola.utils import req_missing

try:
    import wikipediaapi
except ImportError:
    wikipediaapi = None

class WikipediaShortcodePlugin(ShortcodePlugin):
    """Return an HTML element containing the summary of a Wikipedia article that can be styled as a tooltip"""
    
    name = "wikipedia"
    
    def _error(self, msg):
        self.logger.error(msg)
        return '<div class="text-error">{}</div>'.format(msg)

    def handler(self, article, text=None, site=None, data=None, lang='en', post=None):
        if wikipediaapi is None:
            msg = req_missing(['wikipediaapi'], 'use the wikipedia shortcode', optional=True)
            return self._error(msg)
        
        wiki_api = wikipediaapi.Wikipedia("Lorenzo Rovigatti (lorenzo.rovigatti@gmail.com)", lang)
        wiki_page = wiki_api.page(article)
        
        if not wiki_page.exists():
            return self._error('Wikipedia page "{0}" not found'.format(article))
        
        if text is None:
            text = article
            
        url = wiki_page.fullurl
        # we retain only the first paragraph of the summary
        summary = wiki_page.summary.split('\n')[0]
        # and remove the "(listen);" and surrounding whitespace
        summary = "".join(x.strip() for x in summary.split("(listen);"))
        
        tooltip = """
        <span class="wikipedia_tooltip"><a href="{0}" target="_blank">{1}</a>
            <span class="wikipedia_summary">
            <a href="{0}" target="_blank" class="wikipedia_wordmark">
              <img src="https://upload.wikimedia.org/wikipedia/commons/b/bb/Wikipedia_wordmark.svg">
              <span class="wikipedia_icon"></span>
            </a>
            {2}
            </span>
        </span>""".format(url, text, summary)
        
        return tooltip, []
