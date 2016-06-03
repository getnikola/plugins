# -*- coding: utf-8 -*-

# Copyright © 2012-2013 Puneeth Chaganti, Roberto Alsina and others.

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

from __future__ import unicode_literals, print_function
import codecs
from collections import defaultdict
import io
import math
from os.path import relpath
import re
from textwrap import dedent

from nikola.plugin_categories import Command
from nikola.utils import bytes_str, LOGGER, req_missing, sys_decode, unicode_str
from nikola.plugins.compile.ipynb import flag as ipy_flag
if ipy_flag:
    from nikola.plugins.compile.ipynb import current_nbformat, ipy_modern, nbformat


def add_tags(site, tags, filepaths, dry_run=False):
    """ Adds a list of comma-separated tags, given a list of filepaths.

        $ nikola tags --add "foo,bar" posts/*.rst

    The above command will add foo and bar tags to all rst posts.

    """

    tags = _process_comma_separated_tags(tags)

    posts = [post for post in site.timeline if post.source_path in filepaths]

    if len(tags) == 0 or len(posts) == 0:
        print("ERROR: Need at least one tag and post.")
        return

    FMT = 'Tags for {0}:\n{1:>6} - {2}\n{3:>6} - {4}\n'
    OLD = 'old'
    NEW = 'new'

    all_new_tags = []
    for post in posts:
        old_tags = _post_tags(post)
        new_tags = _add_tags(old_tags[:], tags)
        all_new_tags.append(new_tags)

        if dry_run:
            print(FMT.format(
                post.source_path, OLD, old_tags, NEW, new_tags)
            )

        elif new_tags != old_tags:
            _replace_tags(site, post, new_tags)

    return all_new_tags


def list_tags(site, sorting='alpha'):
    """ Lists all the tags used in the site.

    The tags are sorted alphabetically, by default.  Sorting can be
    one of 'alpha' or 'count'.

    """

    posts_per_tag = _posts_per_tag(site)
    if sorting == 'count':
        tags = sorted(posts_per_tag, key=lambda tag: len(posts_per_tag[tag]), reverse=True)
    else:
        tags = sorted(posts_per_tag)

    for tag in tags:
        if sorting == 'count':
            show = '{0:>4} {1}'.format(len(posts_per_tag[tag]), tag)
        else:
            show = tag
        print(show)

    return tags


def merge_tags(site, tags, filepaths, dry_run=False):
    """ Merges a list of comma-separated tags, replacing them with the last tag

    Requires a list of file names to be passed as arguments.

        $ nikola tags --merge "foo,bar,baz,useless" posts/*.rst

    The above command will replace foo, bar, and baz with 'useless'
    in all rst posts.

    """

    tags = _process_comma_separated_tags(tags)

    posts = [post for post in site.timeline if post.source_path in filepaths]

    if len(tags) < 2 or len(posts) == 0:
        print("ERROR: Need at least two tags and a post.")
        return

    FMT = 'Tags for {0}:\n{1:>6} - {2}\n{3:>6} - {4}\n'
    OLD = 'old'
    NEW = 'new'

    all_new_tags = []
    for post in posts:
        old_tags = _post_tags(post)
        new_tags = _clean_tags(old_tags[:], set(tags[:-1]), tags[-1])
        all_new_tags.append(new_tags)

        if dry_run:
            print(FMT.format(
                post.source_path, OLD, old_tags, NEW, new_tags)
            )

        elif new_tags != old_tags:
            _replace_tags(site, post, new_tags)

    return all_new_tags


def remove_tags(site, tags, filepaths, dry_run=False):
    """ Removes a list of comma-separated tags, given a list of filepaths.

        $ nikola tags --remove "foo,bar" posts/*.rst

    The above command will remove foo and bar tags to all rst posts.

    """

    tags = _process_comma_separated_tags(tags)

    posts = [post for post in site.timeline if post.source_path in filepaths]

    if len(tags) == 0 or len(posts) == 0:
        print("ERROR: Need at least one tag and post.")
        return

    FMT = 'Tags for {0}:\n{1:>6} - {2}\n{3:>6} - {4}\n'
    OLD = 'old'
    NEW = 'new'

    if len(posts) == 0:
        new_tags = []

    all_new_tags = []
    for post in posts:
        old_tags = _post_tags(post)
        new_tags = _remove_tags(old_tags[:], tags)
        all_new_tags.append(new_tags)

        if dry_run:
            print(FMT.format(
                post.source_path, OLD, old_tags, NEW, new_tags)
            )

        elif new_tags != old_tags:
            _replace_tags(site, post, new_tags)

    return all_new_tags


def search_tags(site, term):
    """ Lists all tags that match the specified search term.

    The tags are sorted alphabetically, by default.

    """

    posts_per_tag = _posts_per_tag(site)
    search_re = re.compile(term.lower())

    matches = [
        tag for tag in posts_per_tag
        if term in tag.lower() or search_re.match(tag.lower())
    ]

    new_tags = sorted(matches, key=lambda tag: tag.lower())

    for tag in new_tags:
        print(tag)

    return new_tags


def sort_tags(site, filepaths, dry_run=False):
    """ Sorts all the tags in the given list of posts.

        $ nikola tags --sort posts/*.rst

    The above command will sort all tags alphabetically, in all rst
    posts.  This command can be run on all posts, to clean up things.

    """

    posts = [post for post in site.timeline if post.source_path in filepaths]

    if len(posts) == 0:
        LOGGER.error("Need at least one post.")

        return

    FMT = 'Tags for {0}:\n{1:>6} - {2}\n{3:>6} - {4}\n'
    OLD = 'old'
    NEW = 'new'

    all_new_tags = []
    for post in posts:
        old_tags = _post_tags(post)
        new_tags = sorted(old_tags)
        all_new_tags.append(new_tags)

        if dry_run:
            print(FMT.format(
                post.source_path, OLD, old_tags, NEW, new_tags)
            )

        elif new_tags != old_tags:
            _replace_tags(site, post, new_tags)

    return all_new_tags


def _format_doc_string(function):
    text = dedent(' ' * 4 + function.__doc__.strip())
    doc_lines = [line for line in text.splitlines() if line.strip()]
    return '\n'.join(doc_lines) + '\n'


def _post_tags(post):
    """Return the tags of a post, including special tags."""
    tags = post.tags[:]
    if post.is_draft:
        tags.append('draft')

    if post.is_private:
        tags.append('private')

    return tags


def _posts_per_tag(site, include_special=True):
    tags = site.posts_per_tag.copy()
    if not include_special:
        return tags

    skipped_posts = [post for post in site.all_posts if not post.use_in_feeds]
    for post in skipped_posts:
        post_tags = post.tags
        if post.is_draft:
            post_tags.append('draft')
        if post.is_private:
            post_tags.append('private')

        for tag in post_tags:
            if post not in tags[tag]:
                tags[tag].append(post)

    return tags


class CommandTags(Command):

    """ Manage tags on the site.

    This plugin is inspired by `jtags <https://github.com/ttscoff/jtag>`_.
    """

    name = "tags"
    doc_usage = "[-n|--dry-run] command [options] [arguments] [filepath(s)]"
    doc_purpose = "Command to help manage the tags on your site"
    cmd_options = [
        {
            'name': 'add',
            'long': 'add',
            'short': 'a',
            'default': '',
            'type': str,
            'help': _format_doc_string(add_tags)
        },
        {
            'name': 'list',
            'long': 'list',
            'short': 'l',
            'default': False,
            'type': bool,
            'help': _format_doc_string(list_tags)
        },
        {
            'name': 'list_sorting',
            'short': 's',
            'type': str,
            'default': 'alpha',
            'help': 'Changes sorting of list; can be one of alpha or count.\n'
        },
        {
            'name': 'merge',
            'long': 'merge',
            'type': str,
            'default': '',
            'help': _format_doc_string(merge_tags)
        },
        {
            'name': 'remove',
            'long': 'remove',
            'short': 'r',
            'default': '',
            'type': str,
            'help': _format_doc_string(remove_tags)
        },
        {
            'name': 'search',
            'long': 'search',
            'default': '',
            'type': str,
            'help': _format_doc_string(search_tags)
        },
        {
            'name': 'sort',
            'long': 'sort',
            'short': 'S',
            'default': False,
            'type': bool,
            'help': _format_doc_string(sort_tags)
        },
        {
            'name': 'tag',
            'long': 'auto-tag',
            'default': False,
            'type': bool,
            'help': 'Automatically tag a given set of posts.'
        },
        {
            'name': 'dry-run',
            'long': 'dry-run',
            'short': 'n',
            'type': bool,
            'default': False,
            'help': 'Dry run (no files are edited).\n'
        },

    ]

    def _execute(self, options, args):
        """Manage the tags on the site."""

        try:
            self.site.scan_posts(True, True)
        except:
            # old nikola
            self.site.scan_posts()

        self._unicode_options(options)

        filepaths = [relpath(path) for path in args]

        if len(options['add']) > 0 and len(filepaths) > 0:
            add_tags(self.site, options['add'], filepaths, options['dry-run'])

        elif options['list']:
            list_tags(self.site, options['list_sorting'])

        elif options['merge'].count(',') > 0 and len(filepaths) > 0:
            merge_tags(self.site, options['merge'], filepaths, options['dry-run'])

        elif len(options['remove']) > 0 and len(filepaths) > 0:
            remove_tags(self.site, options['remove'], filepaths, options['dry-run'])

        elif len(options['search']) > 0:
            search_tags(self.site, options['search'])

        elif options['tag'] and len(filepaths) > 0:
            tagger = _AutoTag(self.site)
            for post in filepaths:
                tags = ','.join(tagger.tag(post))
                add_tags(self.site, tags, [post], options['dry-run'])

        elif options['sort'] and len(filepaths) > 0:
            sort_tags(self.site, filepaths, options['dry-run'])

        else:
            print(self.help())

    def _unicode_options(self, options):
        for key, value in options.items():
            options[key] = sys_decode(value)


# ### Private definitions ######################################################

class _AutoTag(object):
    """ A class to auto tag posts, using tf-idf. """

    WORDS = '([A-Za-z]+[A-Za-z-]*[A-Za-z]+|[A-Za-z]+)'

    def tag(self, post, count=5):
        """ Return a list of top tags, given a post.

        post: can either be a post object or the source path
        count: the number of tags to return

        """

        if isinstance(post, (bytes_str, unicode_str)):
            source_path = post
            post = self._get_post_from_source_path(source_path)
            if post is None:
                LOGGER.error('No post found for path: %s' % source_path)
                return

        return self._find_top_scoring_tags(post, count)

    # ### 'object' interface ###################################################

    def __init__(self, site, use_nltk=True):
        """ Set up a dictionary of documents.

        Each post is mapped to a list of words it contains.

        """

        self._site = site
        self._documents = {}
        self._stem_cache = {}
        self._use_nltk = use_nltk and self._nltk_available()
        self._tag_set = set([])

        if self._use_nltk:
            from nltk.corpus import stopwords
            from nltk.tokenize import word_tokenize
            from nltk.stem import SnowballStemmer

            self._tag_pattern = re.compile(self.WORDS + '$')
            self._tokenize = word_tokenize
            self._stem_word_mapping = defaultdict(set)
            self._stemmer = SnowballStemmer('porter')
            self._stopwords = set(stopwords.words())

        else:
            self._tag_pattern = re.compile(self.WORDS)

        self._process_tags()
        self._process_posts()
        self._document_count = len(self._documents)

    # ### 'Private' interface ##################################################

    def _find_stems_for_words_in_documents(self, text):
        """ Process text to get list of stems. """

        words = []

        for word in self._tokenize(text):
            if self._tag_pattern.match(word) is not None:
                if word not in self._stopwords:
                    words.append(self._get_stem_from_cache(word))

        return words

    def _find_top_scoring_tags(self, post, count):
        """ Return the tags with the top tf-idf score. """

        tf_idf_table = {}

        for word in self._documents[post.source_path]:
            tf_idf_table[word] = self._tf_idf(word, post)
            tags = sorted(
                tf_idf_table, key=lambda x: tf_idf_table[x], reverse=True
            )

        if self._use_nltk:
            tags = [
                sorted(self._stem_word_mapping[tag], key=len)[0]
                for tag in tags[:count]
            ]

        else:
            tags = tags[:count]

        return tags

    def _get_post_from_source_path(self, source):
        """ Return a post given the source path. """

        posts = [
            post for post in self._site.timeline
            if post.source_path == source
        ]

        post = posts[0] if len(posts) == 1 else None

        return post

    def _get_post_text(self, post):
        """ Return the text of a given post. """

        with codecs.open(post.source_path, 'r', 'utf-8') as post_file:
            post_text = post_file.read().lower()
            if not post.is_two_file:
                post_text = post_text.split('\n\n', 1)[-1]

        return post_text

    def _get_word_count(self, post):
        """ Get the count of all words in a given post. """

        word_counts = defaultdict(lambda: 0)

        for word in self._documents[post.source_path]:
            word_counts[word] += 1

        return word_counts

    def _get_stem_from_cache(self, word):
        """ Return the stem for a word, and cache it, if required. """

        if word not in self._stem_cache:
            stem = self._stemmer.stem(word)
            self._stem_cache[word] = stem
            self._stem_word_mapping[stem].add(word)
        else:
            stem = self._stem_cache[word]

        return stem

    def _modified_inverse_document_frequency(self, word):
        """ Gets the inverse document frequency of a word.

        This departs from the normal inverse document frequency
        calculation, to give a higher score for words that are already
        being used as tags in other posts.
        """

        if word not in self._tag_set:
            count = sum(
                1 for doc in self._documents.values() if word.lower() in doc
            )
        else:
            count = 0.25

        return math.log(self._document_count / float(count))

    @staticmethod
    def _nltk_available():
        """ Return True if we can import nltk. """

        try:
            import nltk
        except ImportError:
            nltk = None

        return nltk is not None

    def _process_posts(self):
        """ Tokenize the posts (and stem the words, if use_nltk). """

        for post in self._site.timeline:

            text = self._get_post_text(post)

            if not self._use_nltk:
                words = self._tag_pattern.findall(text)

            else:
                words = self._find_stems_for_words_in_documents(text)

            self._documents[post.source_path] = words

    def _process_tags(self):
        """ Create a tag set, to be used during tf-idf calculation. """

        tags = self._site.posts_per_tag.keys()

        if not self._use_nltk:
            self._tag_set = set(tags)

        else:
            self._tag_set = set(self._get_stem_from_cache(tag) for tag in tags)

    def _term_frequncy(self, word, post):
        """ Returns the frequency of a word, given a post. """

        word_counts = self._get_word_count(post)

        # A mix of augmented, logarithmic frequency.  We divide with
        # the max frequency to prevent a bias towards longer document.
        tf = math.log(
            1 + float(word_counts[word]) / max(word_counts.values())
        )

        return tf

    def _tf_idf(self, word, post):
        """ Return tf-idf value of a word, in a specified post. """

        tf = self._term_frequncy(word, post)
        idf = self._modified_inverse_document_frequency(word)

        return tf * idf


def _add_tags(tags, additions):
    """ In all tags list, add tags in additions if not already present. """

    for tag in additions:
        if tag not in tags:
            tags.append(tag)

    return tags


def _clean_tags(tags, remove, keep):
    """ In all tags list, replace tags in remove with keep tag. """
    original_tags = tags[:]
    for index, tag in enumerate(original_tags):
        if tag in remove:
            tags.remove(tag)

    if len(original_tags) != len(tags) and keep not in tags:
        tags.append(keep)

    return tags


def _process_comma_separated_tags(tags):
    """ Return a list of tags given a string of comma-separated tags. """
    return [tag.strip() for tag in tags.strip().split(',') if tag.strip()]


def _remove_tags(tags, removals):
    """ In all tags list, remove tags in removals. """

    for tag in removals:
        while tag in tags:
            tags.remove(tag)

    return tags


def _replace_tags(site, post, tags):
    """Chooses the appropriate replace method based on post type."""
    compiler = site.get_compiler(post.source_path)
    if compiler.name == 'ipynb':
        _replace_ipynb_tags(post, tags)

    else:
        _replace_tags_line(post, tags)


def _replace_ipynb_tags(post, tags):
    """Replaces tags in the notebook metadata with the given tags."""
    if ipy_flag is None:
        req_missing(['ipython[notebook]>=2.0.0'], 'build this site (compile ipynb)')

    nb = nbformat.read(post.source_path, current_nbformat)
    metadata = nb['metadata']['nikola']
    metadata['tags'] = ','.join(tags)

    with io.open(post.source_path, "w+", encoding="utf8") as fd:
        if ipy_modern:
            nbformat.write(nb, fd, 4)
        else:
            nbformat.write(nb, fd, 'ipynb')


def _replace_tags_line(post, tags):
    """ Replaces the line that lists the tags, with given tags. """

    if post.is_two_file:
        path = post.metadata_path
        try:
            if not post.newstylemeta:
                LOGGER.error("{0} uses old-style metadata which is not supported by this plugin, skipping.".format(path))
                return
        except AttributeError:
            # post.newstylemeta is not present in older versions.  If the user
            # has old-style meta files, it will crash or not do the job.
            pass
    else:
        path = post.source_path

    with codecs.open(path, 'r', 'utf-8') as f:
        text = f.readlines()

    tag_identifier = u'.. tags:'
    new_tags = u'.. tags: %s\n' % ', '.join(tags)

    for index, line in enumerate(text[:]):
        if line.startswith(tag_identifier):
            text[index] = new_tags
            break

    with codecs.open(path, 'w+', 'utf-8') as f:
        f.writelines(text)
