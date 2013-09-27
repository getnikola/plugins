#!/usr/bin/env python

import codecs
import glob
import json
import os

import colorama

from nikola import utils

def create_site():
    for plugin in glob.glob(os.path.join('plugins', '*')):

        read_plugin(plugin)

def read_plugin(plugin):
    # Gather this plugin's data
    plugin_name = os.path.basename(plugin)
    data = {}
    data['name'] = plugin_name
    readme = os.path.join(plugin, 'README.md')
    if os.path.isfile(readme):
        with codecs.open(readme, 'r', 'utf8') as inf:
            data['readme'] = inf.read()
    else:
        data['readme'] = ''

    plugins = utils.get_plugin_chain(plugin_name)
    data['engine'] = utils.get_template_engine(plugins)

def error(msg):
    print(colorama.Fore.RED + "ERROR:" + msg)

if __name__ == "__main__":
    import commandline
    colorama.init()
    commandline.run_as_main(create_site)
