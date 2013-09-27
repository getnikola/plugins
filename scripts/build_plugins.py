#!/usr/bin/env python

"""Make sanity checks on the provided plugins."""

from __future__ import unicode_literals, print_function
from contextlib import contextmanager
import glob
import json
import os
import subprocess
import colorama
from progressbar import ProgressBar

BASE_URL = "http://plugins.nikola.ralsina.com.ar/v6/"


def error(msg):
    print(colorama.Fore.RED + "ERROR:" + msg)


def plugin_list():
    return [plugin.split('/')[-1] for plugin in glob.glob("plugins/*")]


def build_plugin(plugin=None):
    if plugin is None:  # Check them all
        print("\nBuilding all plugins\n")
        progress = ProgressBar()
        for plugin in progress(plugin_list()):
            build_plugin(plugin)
        return

    if not os.path.isdir(os.path.join("output", "v6")):
        os.mkdir(os.path.join("output", "v6"))

    if os.path.isdir('plugins/' + plugin):
        with cd('plugins/'):
            subprocess.check_call('zip -r ../output/v6/{0}.zip '
                                  '{0}'.format(plugin), stdout=subprocess.PIPE,
                                  shell=True)

    plugins_dict = {}
    for plugin in glob.glob('plugins/*/'):
        t_name = os.path.basename(plugin[:-1])
        plugins_dict[t_name] = BASE_URL + t_name + ".zip"
    with open(os.path.join("output", "v6", "plugins.json"), "wb+") as outf:
        json.dump(plugins_dict, outf, indent=4, ensure_ascii=True,
                  sort_keys=True)


@contextmanager
def cd(path):
    old_dir = os.getcwd()
    os.chdir(path)
    yield
    os.chdir(old_dir)

if __name__ == "__main__":
    import commandline
    colorama.init()
    commandline.run_as_main(build_plugin)
