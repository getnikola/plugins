#!/usr/bin/env python

"""Inspect plugins, create a JSON describing all the data."""

from __future__ import unicode_literals, print_function
import codecs
import glob
import json
import os

import colorama
from progressbar import ProgressBar

import ConfigParser

BASE_URL = "http://plugins.nikola.ralsina.com.ar/v6/"


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
    #readme = utils.get_asset_path('README.md', [plugin])
    #conf_sample = utils.get_asset_path('conf.py.sample', [plugin])
    readme = os.path.join('plugins', plugin, 'README.md')
    conf_sample = os.path.join('plugins', plugin, 'conf.py.sample')
    ini = os.path.join('plugins', plugin, plugin + '.plugin')

    if os.path.exists(ini):
        c = ConfigParser.ConfigParser()
        c.read(ini)
        data['author'] = c.get('Documentation', 'Author')
        data['version'] = c.get('Documentation', 'Version')
        data['description'] = c.get('Documentation', 'Description')
        try:
            data['minver'] = c.get('Documentation', 'min_version')
        except ConfigParser.NoOptionError:
            data['minver'] = None
        try:
            data['maxver'] = c.get('Documentation', 'max_version')
        except ConfigParser.NoOptionError:
            data['maxver'] = None
    else:
        error('Plugin {0} has no .plugin file in the main '
              'directory.'.format(plugin))

    if os.path.exists(readme):
        data['readme'] = codecs.open(readme, 'r', 'utf8').read()
    else:
        data['readme'] = 'No README.md file available.'

    if os.path.exists(conf_sample):
        data['readme'] += ('\n\n**Suggested Configuration:**\n```' +
                           '\n{0}\n```\n\n'.format(codecs.open(
                               conf_sample, 'r', 'utf8').read()))

    return data

if __name__ == "__main__":
    import commandline
    colorama.init()
    commandline.run_as_main(build_site)
