# -*- coding: utf-8 -*-
#
# MIT License
#
# Copyright (c) 2026 Stephane Manet
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import html
import json

from nikola.plugin_categories import ShortcodePlugin  # type: ignore


DEFAULT_CDN_URL = "https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"
DEFAULT_INITIALIZE = {"startOnLoad": False}


class MermaidShortcode(ShortcodePlugin):
    name = "mermaid"

    def handler(self, site=None, data=None, lang=None, **kwargs):
        theme = html.escape(str(kwargs.get("theme", "default")), quote=True)
        content = (data or "").strip()
        settings = _settings(site)

        diagram = (
            f'<div class="mermaid" data-theme="{theme}">\n'
            f'{content}\n'
            '</div>'
        )

        if not settings["auto_load"]:
            return diagram

        return diagram + "\n" + _loader_script(settings)


def _settings(site):
    config = {}
    if site is not None:
        config = site.config.get("MERMAID_CONFIG") or {}

    initialize = config.get("initialize", DEFAULT_INITIALIZE)
    if not isinstance(initialize, dict):
        initialize = DEFAULT_INITIALIZE

    initialize = dict(initialize)
    initialize.setdefault("startOnLoad", False)

    return {
        "auto_load": bool(config.get("auto_load", True)),
        "cdn_url": str(config.get("cdn_url", DEFAULT_CDN_URL)),
        "initialize": initialize,
    }


def _loader_script(settings):
    cdn_url = _to_script_json(settings["cdn_url"])
    initialize = _to_script_json(settings["initialize"], sort_keys=True)

    return (
        '<script>\n'
        '(function () {\n'
        '  function renderMermaid() {\n'
        '    if (!window.mermaid) { return; }\n'
        f'    var config = {initialize};\n'
        '    if (!window.__nikolaMermaidInitialized) {\n'
        '      window.mermaid.initialize(config);\n'
        '      window.__nikolaMermaidInitialized = true;\n'
        '    }\n'
        '    if (window.mermaid.run) {\n'
        '      window.mermaid.run({ querySelector: ".mermaid" });\n'
        '    } else if (window.mermaid.init) {\n'
        '      window.mermaid.init(undefined, document.querySelectorAll(".mermaid"));\n'
        '    }\n'
        '  }\n'
        '  if (window.mermaid) {\n'
        '    renderMermaid();\n'
        '    return;\n'
        '  }\n'
        '  window.__nikolaMermaidReadyCallbacks = window.__nikolaMermaidReadyCallbacks || [];\n'
        '  window.__nikolaMermaidReadyCallbacks.push(renderMermaid);\n'
        '  if (window.__nikolaMermaidLoading) { return; }\n'
        '  window.__nikolaMermaidLoading = true;\n'
        '  var script = document.createElement("script");\n'
        f'  script.src = {cdn_url};\n'
        '  script.onload = function () {\n'
        '    var callbacks = window.__nikolaMermaidReadyCallbacks || [];\n'
        '    window.__nikolaMermaidReadyCallbacks = [];\n'
        '    callbacks.forEach(function (callback) { callback(); });\n'
        '  };\n'
        '  document.head.appendChild(script);\n'
        '}());\n'
        '</script>'
    )


def _to_script_json(value, **kwargs):
    return json.dumps(value, **kwargs).replace("</", "<\\/")
