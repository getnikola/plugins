# Copyright © 2020 Roberto Alsina

from html import escape

from docutils import nodes
from docutils.parsers.rst import Directive, directives

from nikola.plugin_categories import RestExtension


class Plugin(RestExtension):

    name = "rest_prism_js"

    def set_site(self, site):
        self.site = site
        directives.register_directive("code", Code)
        directives.register_directive("code-block", Code)
        return super(Plugin, self).set_site(site)


class Code(Directive):
    has_content = True
    required_arguments = 0
    optional_arguments = 1

    option_spec = {
        "number-lines": directives.unchanged,
        "linenos": directives.unchanged,
    }

    def run(self):
        if self.arguments:
            code_classes = f"language-{self.arguments[0]}" 
        else:
            code_classes = "language-none"

        pre_classes = data_start = ""
        if "linenos" in self.options or "number-lines" in self.options:
            pre_classes = "line-numbers"
            if self.options.get("linenos", self.options.get("line-numbers")):
                data_start = self.options["linenos"]        

        code_classes = f'class="{code_classes}"'
        if pre_classes:
            pre_classes = f'class="{pre_classes}"'
        if data_start:
            data_start = f'data-start="{data_start}"'
        content = "\n".join(escape(l) for l in self.content)

        result = [
            nodes.raw(
                "",
                f'<pre {pre_classes} {data_start}><code {code_classes}>{content}</code></pre>',
                format="html",
            )
        ]
        # from doit.tools import set_trace; set_trace()
        return result
