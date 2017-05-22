# -*- coding: utf-8 -*-

# Copyright © 2017 Roberto Alsina and others.

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

from __future__ import print_function, unicode_literals

import gensim

from nikola.plugin_categories import Task


class Similarity(Task):
    """Calculate post similarity."""
    name = "similarity"

    def set_site(self, site):
        self.site = site

    def gen_tasks(self):
        """Build similarity data for each post."""
        self.site.scan_posts()

        texts = []

        for p in self.site.timeline:
            texts.append(p.text(strip_html=True).lower().split())

        dictionary = gensim.corpora.Dictionary(texts)
        corpus = [dictionary.doc2bow(text) for text in texts]
        lsi = gensim.models.LsiModel(corpus, id2word=dictionary, num_topics=2)
        index = gensim.similarities.MatrixSimilarity(lsi[corpus])

        for i, post in enumerate(self.site.timeline):
            doc = texts[i]
            vec_bow = dictionary.doc2bow(doc)
            vec_lsi = lsi[vec_bow]
            sims = index[vec_lsi]
            sims = sorted(enumerate(sims), key=lambda item: -item[1])
            print(i, sims[:10])
