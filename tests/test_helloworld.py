# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from v7.helloworld.helloworld import Plugin as HelloWorld


class MockObject:
    pass


class TestHelloWorld:
    def test_gen_tasks(self):
        hw = HelloWorld()
        hw.site = MockObject()
        hw.site.config = {}
        for i in hw.gen_tasks():
            assert i['basename'] == 'hello_world'
            assert i['uptodate'] == [False]
            assert isinstance(i['actions'][0][1][0], bool)
