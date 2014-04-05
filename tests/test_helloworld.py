# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import sys
import unittest

sys.path.append(os.path.join('v6', 'helloworld'))

from helloworld import Plugin as HelloWorld
from nikola.utils import LOGGER


class MockObject:
    pass


class TestHelloWorld(unittest.TestCase):
    @staticmethod
    def setUpClass():
        LOGGER.notice('--- TESTS FOR helloworld')

    @staticmethod
    def tearDownClass():
        sys.stdout.write('\n')
        LOGGER.notice('--- END OF TESTS FOR helloworld')

    def test_gen_tasks(self):
        hw = HelloWorld()
        hw.site = MockObject()
        hw.site.config = {}
        for i in hw.gen_tasks():
            self.assertEqual(i['basename'], 'hello_world')
            self.assertEqual(i['uptodate'], [False])
            try:
                self.assertIsInstance(i['actions'][0][1][0], bool)
            except AttributeError:
                LOGGER.warning('Python 2.6 is missing assertIsInstance()')

if __name__ == '__main__':
    unittest.main()
