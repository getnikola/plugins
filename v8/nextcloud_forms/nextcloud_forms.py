# -*- coding: utf-8 -*-

# Copyright © 2022, Andreas Brinner.

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


import os
import json
import base64
import requests

from html.parser import HTMLParser
from urllib.parse import urlparse

from nikola.plugin_categories import ShortcodePlugin


SUBMIT_FORM_JS_PATH = os.path.join(os.path.dirname(__file__), 'submit_form.js')


class FormDataParser(HTMLParser):
    def __init__(self, *args, **argv):
        self.data = {}
        HTMLParser.__init__(self, *args, **argv)

    def handle_starttag(self, tag, attrs):
        if tag == "input":
            data = dict(attrs)
            if "id" in data and "value" in data:
                self.data[data["id"]] = json.loads(base64.b64decode(data["value"]))


class Plugin(ShortcodePlugin):
    """Plugin for nextcloud_forms directive."""

    name = "nextcloud_forms"

    def get_public_form_data(self, link):
        try:
            data = requests.get(link).text
        except requests.exceptions.RequestException:
            self.logger.error('Cannot get form data from url={0}', link)

        parser = FormDataParser()
        parser.feed(data)

        return parser.data

    def generate_ocs_url(self, link):
        """Generate the OCS API base url from the given link.

           see also:
           https://github.com/nextcloud/nextcloud-router/blob/master/lib/index.ts#L29"
        """
        url = urlparse(link)
        return "{}://{}/ocs/v2.php/apps/forms".format(url.scheme, url.netloc)

    def set_site(self, site):
        super(type(self), self).set_site(site)
        with open(SUBMIT_FORM_JS_PATH, "r") as fd:
            submit_form_js = "<script>{}</script>".format(fd.read())
        site.template_hooks['body_end'].append(submit_form_js)

    def handler(self, link, template="nextcloud_forms.tmpl",
                site=None, data=None, lang=None, post=None, **argv):
        """Create HTML for Nextcloud Forms formular."""

        form_data = self.get_public_form_data(link)

        endpoint = self.generate_ocs_url(link)
        endpoint += "/api/v1.1/submission/insert"

        form = form_data.get("initial-state-forms-form")
        if not form:
            self.logger.error('No form defintion fond in url={}'.format(link))

        template_deps = site.template_system.template_deps(template, site.GLOBAL_CONTEXT)
        template_data = site.GLOBAL_CONTEXT.copy()
        template_data.update({
            'lang': lang,
            'form': form,
            'endpoint': endpoint,
            'initial_state': form_data,
            'success_data': data,
        })
        output = site.template_system.render_template(
            template, None, template_data)
        return output, template_deps + [__file__, SUBMIT_FORM_JS_PATH]
