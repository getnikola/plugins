# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sys
import unittest

from nikola.utils import LOGGER
import logbook

from .test_rst_compiler import ReSTExtensionTestCase


class TestBookFigure(ReSTExtensionTestCase):

    extra_plugins_dirs = ["v6/book_figure/"]

    @staticmethod
    def setUpClass():
        LOGGER.notice('--- TESTS FOR book_figure')
        LOGGER.level = logbook.WARNING

    @staticmethod
    def tearDownClass():
        sys.stdout.write('\n')
        LOGGER.level = logbook.NOTICE
        LOGGER.notice('--- END OF TESTS FOR book_figure')

    def test_default(self):
        # the result should be
        expected = (
            '<div class="">'
            '<div class="book-figure-content">'
            '<p class="book-figure-title">Get Nikola</p>'
            '</div></div>'
        )
        self.sample = '.. book_figure:: Get Nikola'
        self.basic_test()
        self.assertEqual(self.html.replace('\n', '').strip(), expected.replace('\n', '').strip())

    def test_full_02(self):
        # the result should be
        expected = (
            '<div class="book-figure">'
            '<div class="book-figure-media">'
            '<a class="book-figure-image" href="http://getnikola.com/" target="_blank">'
            '<img src="http://getnikola.com/galleries/demo/tesla2_lg.jpg" alt="Get Nikola" />'
            '</a></div>'
            '<div class="book-figure-content">'
            '<a class="book-figure-title" href="http://getnikola.com/" target="_blank">Get Nikola</a>'
            '<p class="book-figure-author">by Roberto Alsina</p>'
            '<table class="book-figure-book-number">'
            '<tbody>'
            '<tr><th>ISBN-13:</th><td>1234567890123</td></tr>'
            '<tr><th>ISBN-10:</th><td>1234567890</td></tr>'
            '<tr><th>ASIN:</th><td>B001234567</td></tr>'
            '</tbody></table>'
            '<div class="book-figure-review">'
            '<p>Your review.</p>'
            '</div></div></div>'
        )
        self.sample = """.. book_figure:: Get Nikola
            :class: book-figure
            :url: http://getnikola.com/
            :author: Roberto Alsina
            :isbn_13: 1234567890123
            :isbn_10: 1234567890
            :asin: B001234567
            :image_url: http://getnikola.com/galleries/demo/tesla2_lg.jpg

            Your review.
        """
        self.basic_test()
        self.assertEqual(self.html.replace('\n', '').strip(), expected.replace('\n', '').strip())

    def test_full_03(self):
        # with author url
        # the result should be
        expected = (
            '<div class="book-figure">'
            '<div class="book-figure-media">'
            '<a class="book-figure-image" href="http://getnikola.com/" target="_blank">'
            '<img src="http://getnikola.com/galleries/demo/tesla2_lg.jpg" alt="Get Nikola" />'
            '</a></div>'
            '<div class="book-figure-content">'
            '<a class="book-figure-title" href="http://getnikola.com/" target="_blank">Get Nikola</a>'
            '<p class="book-figure-author">by <a href="http://ralsina.me/" target="_blank">Roberto Alsina</a></p>'
            '<table class="book-figure-book-number">'
            '<tbody>'
            '<tr><th>ISBN-13:</th><td>1234567890123</td></tr>'
            '<tr><th>ISBN-10:</th><td>1234567890</td></tr>'
            '<tr><th>ASIN:</th><td>B001234567</td></tr>'
            '</tbody></table>'
            '<div class="book-figure-review">'
            '<p>Your review.</p>'
            '</div></div></div>'
        )
        self.sample = """.. book_figure:: Get Nikola
            :class: book-figure
            :url: http://getnikola.com/
            :author: Roberto Alsina
            :author_url: http://ralsina.me/
            :isbn_13: 1234567890123
            :isbn_10: 1234567890
            :asin: B001234567
            :image_url: http://getnikola.com/galleries/demo/tesla2_lg.jpg

            Your review.
        """
        self.basic_test()
        self.assertEqual(self.html.replace('\n', '').strip(), expected.replace('\n', '').strip())

if __name__ == '__main__':
    unittest.main()
