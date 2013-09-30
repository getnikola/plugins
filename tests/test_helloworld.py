# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import re
import shutil
import sys
import tempfile
import unittest

from nikola import nikola

sys.path.append(os.path.join('plugins', 'helloworld'))

from helloworld import Plugin as HelloWorld
from nikola.utils import _reload, LOGGER
#import logbook

class MockObject: pass


class TestHelloWorld(unittest.TestCase):

    @staticmethod
    def setUpClass():
        LOGGER.notice('--- TESTS FOR helloworld')
        #LOGGER.level = logbook.WARNING

    @staticmethod
    def tearDownClass():
        sys.stdout.write('\n')
        #LOGGER.level = logbook.NOTICE
        LOGGER.notice('--- END OF TESTS FOR helloworld')

    def test_gen_tasks(self):
        hw = HelloWorld()
        hw.site = MockObject()
        hw.site.config = {}
        for i in hw.gen_tasks():
            self.assertEqual(i['basename'], 'hello_world')
            self.assertEqual(i['uptodate'], [False])
            self.assertIsInstance(i['actions'][0][1][0], bool)

if __name__ == '__main__':
    unittest.main()
