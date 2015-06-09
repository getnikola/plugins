# -*- coding: utf-8 -*-

# Copyright © 2012-2015 Roberto Alsina and others.

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

from __future__ import print_function
import os

from py.path import local
from anyvc import workdir

from nikola.plugin_categories import Command
from nikola.utils import get_logger


def get_path_list(path):
    '''Walk path and return a list of everythin in it.'''
    paths = []
    for root, dirs, files in os.walk(path, followlinks=True):
        for fname in files:
            fpath = os.path.join(root, fname)
            paths.append(fpath)
    return list(set(paths))


class CommandVCS(Command):
    """ Site status. """
    name = "vcs"

    doc_purpose = "display site status"
    doc_description = "Show information about the posts and site deployment."
    logger = None
    cmd_options = []

    def _execute(self, options, args):
        logger = get_logger('vcs', self.site.loghandlers)
        self.site.scan_posts()

        repo_path = local('.')
        wd = workdir.open(repo_path)

        # See if anything got deleted
        del_paths = []
        flag = False
        for s in wd.status():
            if s.state == 'removed':
                if not flag:
                    logger.info('Found deleted files')
                    flag = True
                logger.info('DEL => {}', s.relpath)
                del_paths.append(s.relpath)

        if flag:
            logger.info('Marking as deleted')
            wd.remove(paths=del_paths)
            wd.commit(message='Deleted Files', paths=del_paths)

        # Collect all paths that should be kept under control
        # Post and page sources
        paths = []
        for lang in self.site.config['TRANSLATIONS']:
            for p in self.site.timeline:
                paths.extend(p.fragment_deps(lang))

        # Files in general
        for k, v in self.site.config['FILES_FOLDERS'].items():
            paths.extend(get_path_list(k))
        for k, v in self.site.config['LISTINGS_FOLDERS'].items():
            paths.extend(get_path_list(k))
        for k, v in self.site.config['GALLERY_FOLDERS'].items():
            paths.extend(get_path_list(k))

        # Themes and plugins
        for p in ['plugins', 'themes']:
            paths.extend(get_path_list(p))

        # Add them to the VCS
        paths = list(set(paths))
        wd.add(paths=paths)

        flag = False
        for s in wd.status():
            if s.state == 'added':
                if not flag:
                    logger.info('Found new files')
                    flag = True
                logger.info('NEW => {}', s.relpath)

        logger.info('Committing changes')
        wd.commit(message='Updated files')
