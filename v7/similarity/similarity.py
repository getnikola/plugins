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

import json
import os

import gensim
from stop_words import get_stop_words

from nikola.plugin_categories import Task
from nikola import utils


class Similarity(Task):
    """Calculate post similarity."""
    name = "similarity"

    def set_site(self, site):
        self.site = site

    def gen_tasks(self):
        """Build similarity data for each post."""
        self.site.scan_posts()

        kw = {
            "translations": self.site.translations,
            "output_folder": self.site.config["OUTPUT_FOLDER"],
        }


        stopwords = {}
        for l in self.site.translations:
            stopwords[l] = get_stop_words(l)

        def split_text(text, lang="en"):
            words = text.lower().split()
            return [w for w in words if w not in stopwords[lang]]

        texts = []

        yield self.group_task()

        def tags_similarity(p1, p2):
            t1 = set(p1.tags)
            t2 = set(p2.tags)
            if not (t1 and t2):
                return 0
            # Totally making this up
            return 2.0 * len(t1.intersection(t2)) / (len(t1) + len(t2))

        def title_similarity(p1, p2):
            t1 = set(split_text(p1.title()))
            t2 = set(split_text(p2.title()))
            if not (t1 and t2):
                return 0
            # Totally making this up
            return 2.0 * len(t1.intersection(t2)) / (len(t1) + len(t2))

        indexes = {}
        dictionaries = {}
        lsis = {}

        def create_idx(indexes, dictionaries, lsis, lang):
            texts = []
            for p in self.site.timeline:
                texts.append(split_text(p.text(strip_html=True, lang=lang), lang=lang))
            dictionary = gensim.corpora.Dictionary(texts)
            corpus = [dictionary.doc2bow(text) for text in texts]
            lsi = gensim.models.LsiModel(corpus, id2word=dictionary, num_topics=2)
            index = gensim.similarities.MatrixSimilarity(lsi[corpus])
            indexes[lang] = indexes
            dictionaries[lang] = dictionary
            lsis[lang] = lsi

        def write_similar(path, p, lang, indexes=indexes, dictionaries=dictionaries, lsis=lsis):
            if lang not in dictionaries:
                create_idx(indexes, dictionaries, lsis, lang)
            doc = split_text(p.text(lang), lang)
            vec_bow = dictionaries[lang].doc2bow(doc)
            vec_lsi = lsis[lang][vec_bow]
            body_sims = indexes[lang][vec_lsi]
            tag_sims = [tags_similarity(post, p) for p in self.site.timeline]
            title_sims = [title_similarity(post, p) for p in self.site.timeline]
            full_sims = [tag_sims[i] + title_sims[i] + body_sims[i] * 1.5 for i in range(len(self.site.timeline))]
            full_sims = sorted(enumerate(full_sims), key=lambda item: -item[1])
            related = [(self.site.timeline[s[0]], s[1], tag_sims[s[0]], title_sims[s[0]], body_sims[s[0]]) for s in
                       full_sims[:11] if s[0] != i]
            data = []
            for p, score, tag, title, body in related:
                data.append({
                    'url': '/' + p.destination_path(sep='/'),
                    'title': p.title(),
                    'score': score,
                    'detailed_score': [tag, title, float(body)],
                })
            with open(path, 'w+') as outf:
                json.dump(data, outf)


        for lang in self.site.translations:
            file_dep = []
            for p in self.site.timeline:
                file_dep.append(p.translated_source_path(lang))
            for i, post in enumerate(self.site.timeline):
                out_name = os.path.join(kw['output_folder'], post.destination_path(lang=lang)) + '.related.json'
                task = {
                    'basename': self.name,
                    'name': out_name,
                    'targets': [out_name],
                    'actions': [(write_similar, (out_name, post, lang))],
                    'file_dep': file_dep,
                    'uptodate': [utils.config_changed({1: kw}, 'similarity')],
                }
                yield task

