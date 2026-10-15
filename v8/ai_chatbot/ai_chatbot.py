# -*- coding: utf-8 -*-

# Copyright (c) 2026 Asyntai

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

"""Add the Asyntai AI chatbot to every page of a Nikola site.

The plugin registers the ordinary Asyntai embed snippet on the ``body_end``
template hook, so it lands in front of the closing body tag of every page,
post, index, tag page and archive. Nothing else about the site changes: no
theme files are overridden and no CSS is added.

conf.py::

    ASYNTAI_WIDGET_ID = "asyntai_1a2b3c4d5e6f"
"""

import re

from nikola.plugin_categories import ConfigPlugin
from nikola.utils import get_logger

DEFAULT_SCRIPT_URL = "https://widget.asyntai.com/static/js/chat-widget.js"
WIDGET_ID_PATTERN = re.compile(r"^asyntai_[A-Za-z0-9]+$")

LOGGER = get_logger("ai_chatbot")


def build_tag(widget_id, script_url):
    """Return the embed snippet for one widget."""
    return '<script async src="{src}" data-asyntai-id="{wid}"></script>'.format(
        src=script_url.replace("&", "&amp;").replace('"', "&quot;"),
        wid=widget_id,
    )


def _setting_text(value):
    """Return every language variant of a (possibly translatable) setting as one string."""
    if value is None:
        return ""
    variants = getattr(value, "values", None)
    if isinstance(variants, dict):
        return "\n".join(str(v) for v in variants.values())
    return str(value)


class AiChatbot(ConfigPlugin):
    """Add the Asyntai AI chatbot to every page."""

    name = "ai_chatbot"

    def set_site(self, site):
        """Register the widget snippet on the body_end template hook."""
        super().set_site(site)
        config = site.config

        widget_id = str(config.get("ASYNTAI_WIDGET_ID") or "").strip()
        if not widget_id:
            # set_site runs for every nikola command, also `nikola help` and
            # `nikola plugin`, so a missing ID must never stop those. Say how
            # to fix it and leave the site as it is.
            LOGGER.error(
                "ASYNTAI_WIDGET_ID is not set in conf.py, so the chatbot is not "
                "added. Copy the widget ID from the Install page of your Asyntai "
                "dashboard, for example: ASYNTAI_WIDGET_ID = \"asyntai_1a2b3c4d5e6f\""
            )
            return
        if not WIDGET_ID_PATTERN.match(widget_id):
            LOGGER.error(
                "ASYNTAI_WIDGET_ID \"{0}\" does not look like a widget ID, so the "
                "chatbot is not added. It starts with asyntai_, for example "
                "asyntai_1a2b3c4d5e6f.".format(widget_id)
            )
            return

        # The site owner already pasted the snippet into BODY_END or
        # EXTRA_HEAD_DATA. Two loaders would only fight over one chat bubble,
        # so keep theirs.
        pasted = _setting_text(config.get("BODY_END")) + _setting_text(
            config.get("EXTRA_HEAD_DATA")
        )
        if "data-asyntai-id" in pasted:
            LOGGER.info(
                "The Asyntai snippet is already in BODY_END or EXTRA_HEAD_DATA; "
                "the plugin does not add a second one."
            )
            return

        script_url = str(config.get("ASYNTAI_SCRIPT_URL") or "").strip() or DEFAULT_SCRIPT_URL
        tag = build_tag(widget_id, script_url)
        body_end = config.get("BODY_END")
        variants = getattr(body_end, "values", None)
        if isinstance(variants, dict):
            # BODY_END is the setting every theme prints before </body>, and
            # every Nikola renderer (posts, indexes, archives, tags,
            # galleries) counts it as a dependency, so a new widget ID
            # rebuilds the whole site. Template hooks are not tracked by all
            # of them. The site's GLOBAL_CONTEXT holds this same object, so
            # changing it in place reaches every template.
            # Read every language first: a language with no own value falls
            # back through the dict's default factory, and that read would
            # otherwise see the half-changed setting.
            langs = set(variants) | set(config.get("TRANSLATIONS") or {})
            originals = dict((lang, body_end(lang)) for lang in langs)
            factory = variants.default_factory
            fallback = factory() if factory else ""
            for lang, text in originals.items():
                variants[lang] = (text or "") + "\n" + tag
            variants.default_factory = lambda: (fallback or "") + "\n" + tag
        else:
            # Not a translatable setting (an unusual Nikola build): fall back
            # to the body_end template hook.
            site.template_hooks["body_end"].append(tag)
