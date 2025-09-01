from __future__ import unicode_literals
from nikola.plugin_categories import ConfigPlugin


class HideInputCells(ConfigPlugin):
    def set_site(self, site):
        site.template_hooks['extra_head'].append(
            """
            <!--Code inserted by HideInputCells -->
            <style type="text/css">
              div.input {
                  display: none;
              }
              div.prompt {
                  display: none;
              }
            </style>
            """
        )
        return super(HideInputCells, self).set_site(site)
