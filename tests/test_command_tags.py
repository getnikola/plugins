# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import re
import shutil
import sys

import pytest
from pytest import fixture

from nikola import nikola
from tests import V7_PLUGIN_PATH

try:
    from freezegun import freeze_time
    _freeze_time = True
except ImportError:
    _freeze_time = False
    freeze_time = lambda x: lambda y: y

from v7.tags.tags import (
    _AutoTag, add_tags, list_tags, merge_tags, remove_tags, search_tags,
    sort_tags
)
from nikola.utils import _reload

DEMO_TAGS = ['python', 'demo', 'nikola', 'blog']


class TestCommandTagsBase:

    def _add_test_post(self, title, tags):
        self._run_command(['new_post', '-t', title, '--tags', ','.join(tags)])

    def _force_scan(self):
        self._site._scanned = False
        self._site.scan_posts(True)

    @fixture(autouse=True)
    def _init_site(self, monkeypatch, tmp_path):
        from nikola.plugins.command.init import CommandInit

        monkeypatch.chdir(tmp_path)
        command_init = CommandInit()
        command_init.execute(options={'demo': True, 'quiet': True}, args=['demo'])

        sys.path.insert(0, '')
        monkeypatch.chdir(tmp_path / 'demo')
        import conf  # noqa
        _reload(conf)
        sys.path.pop(0)

        self._site = nikola.Nikola(**conf.__dict__)
        self._site.init_plugins()

    def _parse_new_tags(self, source):
        """ Returns the new tags for a post, given it's source path. """
        self._force_scan()
        posts = [
            post for post in self._site.timeline
            if post.source_path == source
        ]
        return posts[0].tags

    def _run_command(self, args=[]):
        from nikola.__main__ import main
        return main(args)

    def _scan_posts(self):
        self._site.scan_posts()


class TestCommandTagsHelpers(TestCommandTagsBase):
    """ Test all the helper functions used in the plugin.

    Note: None of the tests call the actual Nikola command CommandTags.

    """

    @fixture(autouse=True)
    def setUp(self):
        self._site.scan_posts()

    # ### `TestCommandTagsHelpers` protocol ###################################

    def test_add(self):
        posts = [os.path.join('posts', post) for post in os.listdir('posts')]
        tags = 'test_nikola'

        new_tags = add_tags(self._site, tags, posts)
        new_parsed_tags = self._parse_new_tags(posts[0])

        assert 'test_nikola' in new_tags[0]
        assert set(new_tags[0]) == set(new_parsed_tags)

    def test_add_dry_run(self):
        posts = [os.path.join('posts', post) for post in os.listdir('posts')]
        tags = 'test_nikola'

        new_tags = add_tags(self._site, tags, posts, dry_run=True)
        new_parsed_tags = self._parse_new_tags(posts[0])

        assert 'test_nikola' in new_tags[0]
        assert set(new_parsed_tags) == set(DEMO_TAGS)

    def test_auto_tag_basic(self):
        post = os.path.join('posts', os.listdir('posts')[0])
        tagger = _AutoTag(self._site, use_nltk=False)

        # regexp to check for invalid characters in tags allow only
        # A-Za-z and hyphens.  regexp modified to make sure the whole
        # tag matches, the requirement.
        tag_pattern = re.compile('^' + _AutoTag.WORDS + '$')

        # simple tagging test.
        tags = tagger.tag(post)
        tags = [tag for tag in tags if tag_pattern.search(tag)]
        assert len(tags) == 5

    def test_auto_tag_nltk(self):
        post = os.path.join('posts', os.listdir('posts')[0])
        tagger = _AutoTag(self._site)

        # regexp to check for invalid characters in tags allow only
        # A-Za-z and hyphens.  regexp modified to make sure the whole
        # tag matches, the requirement.
        tag_pattern = re.compile('^' + _AutoTag.WORDS + '$')

        # tagging with nltk.
        nltk_tags = tagger.tag(post)
        tags = [tag for tag in nltk_tags if tag_pattern.search(tag)]
        assert len(tags) == 5

    def test_list(self):
        assert list_tags(self._site) == sorted(DEMO_TAGS)

    def test_list_count_sorted(self):
        self._add_test_post(title='2', tags=['python'])
        self._force_scan()
        tags = list_tags(self._site, 'count')
        assert tags[0] == 'python'

    def test_list_draft(self):
        self._add_test_post(title='2', tags=['python', 'draft'])
        self._force_scan()
        tags = list_tags(self._site)
        assert 'draft' in tags

    def test_list_draft_post_tags(self):
        self._add_test_post(title='2', tags=['ruby', 'draft'])
        self._force_scan()
        tags = list_tags(self._site)
        assert 'ruby' in tags

    @pytest.mark.skipif(not _freeze_time, reason='freezegun package not installed.')
    def test_list_scheduled_post_tags(self):
        with freeze_time("2012-01-14"):
            self._force_scan()
            tags = list_tags(self._site)
            assert 'python' in tags

    def test_merge(self):
        posts = [os.path.join('posts', post) for post in os.listdir('posts')]
        tags = 'nikola, python'

        new_tags = merge_tags(self._site, tags, posts)
        new_parsed_tags = self._parse_new_tags(posts[0])

        assert 'nikola' not in new_tags
        assert set(new_tags[0]) == set(new_parsed_tags)

    def test_merge_dry_run(self):
        posts = [os.path.join('posts', post) for post in os.listdir('posts')]
        tags = 'nikola, python'

        new_tags = merge_tags(self._site, tags, posts, dry_run=True)
        new_parsed_tags = self._parse_new_tags(posts[0])

        assert 'nikola' not in new_tags[0]
        assert set(new_parsed_tags) == set(DEMO_TAGS)

    def test_remove(self):
        posts = [os.path.join('posts', post) for post in os.listdir('posts')]
        tags = 'nikola'

        new_tags = remove_tags(self._site, tags, posts)
        new_parsed_tags = self._parse_new_tags(posts[0])

        assert 'nikola' not in new_tags
        assert set(new_tags[0]) == set(new_parsed_tags)

    def test_remove_draft(self):
        self._add_test_post(title='2', tags=['draft'])
        self._force_scan()
        posts = [os.path.join('posts', post) for post in os.listdir('posts')]

        remove_tags(self._site, 'draft', posts)
        self._force_scan()

        tags = list_tags(self._site, 'count')
        assert 'draft' not in tags

    def test_remove_invalid(self):
        posts = [os.path.join('posts', post) for post in os.listdir('posts')]
        tags = 'wordpress'

        new_tags = remove_tags(self._site, tags, posts)
        new_parsed_tags = self._parse_new_tags(posts[0])

        assert set(new_tags[0]) == set(new_parsed_tags)

    def test_remove_dry_run(self):
        posts = [os.path.join('posts', post) for post in os.listdir('posts')]
        tags = 'nikola'

        new_tags = remove_tags(self._site, tags, posts, dry_run=True)
        new_parsed_tags = self._parse_new_tags(posts[0])

        assert 'nikola' not in new_tags[0]
        assert set(new_parsed_tags) == set(DEMO_TAGS)

    def test_search(self):
        search_terms = {
            'l': ['blog', 'nikola'],
            '.*': sorted(DEMO_TAGS),
            '^ni.*': ['nikola']
        }
        for term in search_terms:
            tags = search_tags(self._site, term)
            assert tags == search_terms[term]

    def test_sort(self):
        posts = [os.path.join('posts', post) for post in os.listdir('posts')]

        new_tags = sort_tags(self._site, posts)
        new_parsed_tags = self._parse_new_tags(posts[0])

        assert new_parsed_tags == sorted(DEMO_TAGS)
        assert new_tags[0] == sorted(DEMO_TAGS)

    def test_sort_dry_run(self):
        posts = [os.path.join('posts', post) for post in os.listdir('posts')]

        old_parsed_tags = self._parse_new_tags(posts[0])
        new_tags = sort_tags(self._site, posts, dry_run=True)
        new_parsed_tags = self._parse_new_tags(posts[0])

        assert old_parsed_tags == new_parsed_tags
        assert new_tags[0] == sorted(DEMO_TAGS)


class TestCommandTags(TestCommandTagsBase):
    """ Tests that directly call the Nikola command CommandTags. """

    # ### `TestCommandTags` protocol ###########################################

    def test_list_count_sorted(self):
        self._add_test_post(title='2', tags=['python'])
        tags = self._run_shell_command(['nikola', 'tags', '-l', '-s', 'count'])
        assert 'python' in tags
        assert tags.split()[1] == 'python'

    @pytest.mark.skipif(sys.version_info[0] == 3, reason='Py2.7 specific bug.')
    def test_merge_unicode_tags(self):
        # Regression test for #63
        exit_code = self._run_command(['tags', '--merge', u'paran\xe3,parana'.encode('utf8'), 'posts/1.rst'])
        assert exit_code == 0

    # ### `Private` protocol ###########################################

    @fixture(autouse=True)
    def _copy_plugin_to_site(self, _init_site):
        if not os.path.exists('plugins'):
            os.makedirs('plugins')
        shutil.copytree(str(V7_PLUGIN_PATH / 'tags'), os.path.join('plugins', 'tags'))

    def _run_shell_command(self, args):
        import subprocess
        try:
            output = subprocess.check_output(args)
        except (OSError, subprocess.CalledProcessError):
            return ''
        else:
            return output.decode('utf-8')
