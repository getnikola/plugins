# -*- coding: utf-8 -*-

# Copyright © 2014 Daniel Aleksandersen.
# Copyright © 2012-2014 Roberto Alsina and others.

# Permission is hereby granted, free of charge, to any
# person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the
# Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the
# Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice
# shall be included in all copies or substantial portions of
# the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
# KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
# PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS
# OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from __future__ import unicode_literals, print_function
import os
try:
    from urlparse import urljoin
except ImportError:
    from urllib.parse import urljoin  # NOQA

import io

from nikola import utils
from nikola.plugin_categories import Task


class windows_live_tiles(Task):
    """Generate Windows Live Tiles."""

    # Custom tiles for websites
    #     http://msdn.microsoft.com/en-us/library/ie/dn455106(v=vs.85).aspx
    # Browser config
    #     http://msdn.microsoft.com/en-us/library/ie/dn320426(v=vs.85).aspx
    # Tile templates
    #     http://msdn.microsoft.com/en-us/library/windows/apps/Hh761491.aspx

    name = "windows_live_tiles"

    def gen_tasks(self):
        """Generate Windows Live Tiles and notifications."""
        kw = {
            "default_lang": self.site.config["DEFAULT_LANG"],
            "site_url": self.site.config["BASE_URL"],
            "output_folder": self.site.config["OUTPUT_FOLDER"],
            "show_untranslated_posts": self.site.config["SHOW_UNTRANSLATED_POSTS"],
            "windows_live_tiles": self.site.config["WINDOWS_LIVE_TILES"],
        }

        msapplication_assets = os.path.join(kw["output_folder"], "assets", "msapplication")
        if not os.path.exists(msapplication_assets):
            os.makedirs(msapplication_assets)

        self.site.scan_posts()
        yield self.group_task()

        deps = []
        if kw["show_untranslated_posts"]:
            posts = self.site.posts[:5]
        else:
            posts = [x for x in self.site.posts if x.is_translation_available(kw["default_lang"])][:5]
        for post in posts:
            deps += post.deps(kw["default_lang"])

        if not len(posts) >= 5:
            utils.LOGGER.warn("The site should have a minimum of five posts to generate Live Tiles!")

        output_name = os.path.join(kw["output_folder"], "browserconfig.xml")
        yield {
            "basename": "windows_live_tiles",
            "name": os.path.normpath(output_name),
            "file_dep": deps,
            "targets": [output_name],
            "actions": [(self.generate_browserconfig,
                           (output_name,
                           kw["windows_live_tiles"]))],

            "task_dep": ["render_posts"],
            "clean": True,
                "uptodate": [utils.config_changed(kw)],
        }

        for i, post in zip(range(len(posts)), posts):
            notification_deps = post.deps(kw["default_lang"])
            output_name = os.path.join(msapplication_assets, "tile_notification" + str(i + 1) + ".xml")
            titles = {
                "maintitle": post.title(kw["default_lang"]),
                "title1": posts[0].title(kw["default_lang"]),
                "title2": posts[1].title(kw["default_lang"]),
                "title3": posts[2].title(kw["default_lang"])
            }

            yield {
                "basename": "windows_live_tiles",
                "name": os.path.normpath(output_name),
                "file_dep": notification_deps,
                "targets": [output_name],
                "actions": [(self.generate_notification_tile, (output_name, kw["default_lang"], kw["windows_live_tiles"]["tileimages"], titles, post.meta[kw["default_lang"]]["previewimage"]))],
                "task_dep": ["render_posts"],
                "clean": True,
                    "uptodate": [utils.config_changed(kw)],
            }

    def generate_notification_tile(self, output_name, lang, tile_templates, titles, image):
        tiledata = """<?xml version="1.0" encoding="utf-8"?>
<tile>
    <visual lang="{lang}" version="2">""".format(lang=lang)
        if "square150x150logo" in tile_templates:
            if image:
                image_url = urljoin(self.site.config["BASE_URL"], image)
                tiledata += """
        <binding template="TileSquare150x150PeekImageAndText04" branding="name">
            <image id="1" src="{image}"/>
            <text id="1">{maintitle}</text>
        </binding>""".format(maintitle=titles["maintitle"], image=image_url)
            else:
                tiledata += """
        <binding template="TileSquare150x150Text04" branding="name">
            <text id="1">{maintitle}</text>
        </binding>""".format(maintitle=titles["maintitle"])

        if "wide310x150logo" in tile_templates:
            if image:
                tiledata += """
        <binding template="TileWide310x150PeekImage03" branding="name">
            <image id="1" src="{image}"/>
            <text id="1">{maintitle}</text>
        </binding>""".format(maintitle=titles["maintitle"], image=image_url)
            else:
                tiledata += """
        <binding template="TileWide310x150Text03" branding="name">
            <text id="1">{maintitle}</text>
        </binding>""".format(maintitle=titles["maintitle"])

        # Giant tile is only included in the first notification, not rotated
        if "square310x310logo" in tile_templates and titles["maintitle"] == titles["title1"]:
            tiledata += """
        <binding template="TileSquare310x310TextList02" branding="name">
            <text id="1">{title1}</text>
            <text id="2">{title2}</text>
            <text id="3">{title3}</text>
        </binding>""".format(title1=titles["title1"], title2=titles["title2"], title3=titles["title3"])

        tiledata += """
    </visual>
</tile>"""

        with io.open(output_name, "w+", encoding="utf8") as outf:
            outf.write(tiledata)

    def generate_browserconfig(self, output_name, windows_live_tiles):
        msapplication_asset_url = urljoin(self.site.config["BASE_URL"], "assets/msapplication/")
        if "frequency" in windows_live_tiles:
            frequency = windows_live_tiles["frequency"]
        else:
            frequency = "720"
        if "tilecolor" in windows_live_tiles:
            tilecolor = windows_live_tiles["tilecolor"]
        else:
            tilecolor = "#ff80aa"

        tiles = ""
        for tiletemplate, tileimage in windows_live_tiles["tileimages"].items():
            tiles += '<{tiletemplate} src="{tileimage}"/>\n        '.format(tiletemplate=tiletemplate, tileimage=urljoin(self.site.config["BASE_URL"], tileimage))

        browserconfig = """<?xml version="1.0" encoding="utf-8"?>
<browserconfig>
   <msapplication>
     <tile>
        {tiles}<TileColor>{tilecolor}</TileColor>
     </tile>
     <notification>
        <polling-uri  src="{msapplication_asset_url}tile_notification1.xml"/>
        <polling-uri2 src="{msapplication_asset_url}tile_notification2.xml"/>
        <polling-uri3 src="{msapplication_asset_url}tile_notification3.xml"/>
        <polling-uri4 src="{msapplication_asset_url}tile_notification4.xml"/>
        <polling-uri5 src="{msapplication_asset_url}tile_notification5.xml"/>
        <frequency>{frequency}</frequency>
        <cycle>5</cycle>
     </notification>
   </msapplication>
</browserconfig>
""".format(tiles=tiles, tilecolor=tilecolor, msapplication_asset_url=msapplication_asset_url, frequency=frequency)
        with io.open(output_name, "w+", encoding="utf8") as outf:
            outf.write(browserconfig)
