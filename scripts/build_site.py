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


def error(msg):
    print(colorama.Fore.RED + "ERROR:" + msg)


def plugin_list():
    return [plugin.split('/')[-1] for plugin in glob.glob("plugins/*")]


def build_site():
    data = {}
    for plugin in plugin_list():
        data[plugin] = get_data(plugin)

    # FIXME check if version is supported by the plugin
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


def build_plugin(plugin=None, version='7'):
    if plugin is None:  # Check them all
        print("\nBuilding all plugins for version {0}\n".format(version))
        for plugin in plugin_list():
            build_plugin(plugin, version)
        return

    if not os.path.isdir(os.path.join("output", "v" + version)):
        os.mkdir(os.path.join("output", "v" + version))

    if os.path.isdir('plugins/' + plugin):
        with cd('plugins/'):
            subprocess.check_call('zip -r ../output/v{0}/{1}.zip {1}'.format(version, plugin),
                                  stdout=subprocess.PIPE,
                                  shell=True)

    plugins_dict = {}
    for plugin in glob.glob('plugins/*/'):
        t_name = os.path.basename(plugin[:-1])
        plugins_dict[t_name] = BASE_URL + t_name + ".zip"
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
    for version in '6', '7':
        build_plugin(None, version)
    build_site()
