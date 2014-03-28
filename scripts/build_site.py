#!/usr/bin/env python

"""Inspect plugins, create a JSON describing all the data."""

from __future__ import unicode_literals, print_function
import codecs
import glob
import json
import os

import colorama
from progressbar import ProgressBar

import pygments
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter

import ConfigParser

BASE_URL = "http://plugins.getnikola.com/v6/"


def error(msg):
    print(colorama.Fore.RED + "ERROR:" + msg)


def plugin_list():
    return [plugin.split('/')[-1] for plugin in glob.glob("plugins/*")]


def build_site():
    data = {}
    progress = ProgressBar()
    for plugin in progress(plugin_list()):
        data[plugin] = get_data(plugin)
    with open(os.path.join('output', 'v6', 'plugin_data.js'), 'wb+') as outf:
        outf.write("var data = " + json.dumps(data, indent=4,
                                              ensure_ascii=True,
                                              sort_keys=True))


def get_data(plugin):
    data = {}
    data['name'] = plugin
    readme = os.path.join('plugins', plugin, 'README.md')
    conf_sample = os.path.join('plugins', plugin, 'conf.py.sample')
    ini = os.path.join('plugins', plugin, plugin + '.plugin')
    reqpy = os.path.join('plugins', plugin, 'requirements.txt')
    reqnonpy = os.path.join('plugins', plugin, 'requirements-nonpy.txt')

    if os.path.exists(ini):
        c = ConfigParser.ConfigParser()
        c.read(ini)
        data['author'] = c.get('Documentation', 'Author')
        data['version'] = c.get('Documentation', 'Version')
        data['description'] = c.get('Documentation', 'Description')
        try:
            data['minver'] = c.get('Nikola', 'MinVersion')
        except ConfigParser.NoOptionError:
            data['minver'] = None
        except ConfigParser.NoSectionError:
            data['maxver'] = None
        try:
            data['maxver'] = c.get('Nikola', 'MaxVersion')
        except ConfigParser.NoOptionError:
            data['maxver'] = None
        except ConfigParser.NoSectionError:
            data['maxver'] = None
        try:
            data['tests'] = c.get('Core', 'Tests')
        except ConfigParser.NoOptionError:
            data['tests'] = None
    else:
        error('Plugin {0} has no .plugin file in the main '
              'directory.'.format(plugin))

    if os.path.exists(readme):
        data['readme'] = codecs.open(readme, 'r', 'utf8').read()
    else:
        data['readme'] = 'No README.md file available.'

    if os.path.exists(conf_sample):
        data['confpy'] = pygments.highlight(
            codecs.open(conf_sample, 'r', 'utf8').read(),
            PythonLexer(), HtmlFormatter(cssclass='code'))
    else:
        data['confpy'] = None

    if os.path.exists(reqpy):
        data['pyreqs'] = codecs.open(reqpy, 'r', 'utf8').readlines()
    else:
        data['pyreqs'] = []

    if os.path.exists(reqnonpy):
        r = codecs.open(reqnonpy, 'r', 'utf8').readlines()

        data['nonpyreqs'] = [i.strip().split('::') for i in r]
    else:
        data['nonpyreqs'] = []

    return data

if __name__ == "__main__":
    import commandline
    colorama.init()
    commandline.run_as_main(build_site)
