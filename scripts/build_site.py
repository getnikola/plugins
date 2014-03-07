#!/usr/bin/env python

"""Inspect plugins, create a JSON describing all the data."""

from __future__ import unicode_literals, print_function
import codecs
from contextlib import contextmanager
import glob
import json
import os
import subprocess

import colorama
import pygments
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter

import ConfigParser

BASE_URL = "http://plugins.getnikola.com/v{0}/"
MINIMUM_VERSION_SUPPORTED = 6
MAXIMUM_VERSION_SUPPORTED = 7
ALL_VERSIONS = list(range(MINIMUM_VERSION_SUPPORTED, MAXIMUM_VERSION_SUPPORTED + 1))


def error(msg):
    print(colorama.Fore.RED + "ERROR:" + msg)


def plugin_list():
    return [plugin.split('/')[-1] for plugin in glob.glob("plugins/*")]


def build_site():
    print("Building plugin_data.js")
    data = {}
    for plugin in plugin_list():
        data[plugin] = get_data(plugin)

    data.update({'__meta__': {'allver': ALL_VERSIONS}})

    with open(os.path.join('output', 'plugin_data.js'), 'wb+') as outf:
        outf.write("var data = " + json.dumps(data, indent=4,
                                              ensure_ascii=True,
                                              sort_keys=True))


def get_data(plugin):
    data = {}
    data['name'] = plugin
    #readme = utils.get_asset_path('README.md', [plugin])
    #conf_sample = utils.get_asset_path('conf.py.sample', [plugin])
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
        except (ConfigParser.NoOptionError, ConfigParser.NoSectionError):
            data['minver'] = None
        try:
            data['maxver'] = c.get('Nikola', 'MaxVersion')
        except (ConfigParser.NoOptionError, ConfigParser.NoSectionError):
            data['maxver'] = None

        if data['minver']:
            minver = data['minver'].split('.')[0]
        else:
            minver = ALL_VERSIONS[0]
        if data['maxver']:
            maxver = data['maxver'].split('.')[0]
        else:
            maxver = ALL_VERSIONS[-1]

        data['allver'] = list(range(int(minver), int(maxver) + 1))

        try:
            data['tests'] = c.get('Core', 'Tests')
        except (ConfigParser.NoOptionError, ConfigParser.NoSectionError):
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


def build_plugin(plugin, version):
    print("Zipping plugin {0} for version {1}".format(plugin, version))

    if not os.path.isdir(os.path.join("output", "v" + version)):
        os.mkdir(os.path.join("output", "v" + version))

    if os.path.isdir('plugins/' + plugin):
        with cd('plugins/'):
            subprocess.check_call('zip -r ../output/v{0}/{1}.zip {1}'.format(version, plugin),
                                  stdout=subprocess.PIPE,
                                  shell=True)


def build_plugins_json(version):
    print("Building plugins.json for version {0}".format(version))
    plugins_dict = {}
    for plugin in plugin_list():
        data = get_data(plugin)

        if ((data['minver'] is None or data['minver'].split('.')[0] <= version) and
           (data['maxver'] is None or data['maxver'].split('.')[0] >= version)):
            plugins_dict[plugin] = BASE_URL.format(version) + plugin + ".zip"
            build_plugin(plugin, version)

    with open(os.path.join("output", "v" + version, "plugins.json"), "wb+") as outf:
        json.dump(plugins_dict, outf, indent=4, ensure_ascii=True,
                  sort_keys=True)


@contextmanager
def cd(path):
    old_dir = os.getcwd()
    os.chdir(path)
    yield
    os.chdir(old_dir)

if __name__ == "__main__":
    colorama.init()
    build_site()
    for version in ALL_VERSIONS:
        build_plugins_json(str(version))
