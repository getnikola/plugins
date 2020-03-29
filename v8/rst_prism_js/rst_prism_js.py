# Copyright © 2020 Roberto Alsina

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
        classes = []
        if self.arguments:
            classes.append("language-" + self.arguments[0])
        else:
            classes.append("language-none")

        if "linenos" or "number-lines" in self.options:
            classes.append("line-numbers")
            if self.options.get("linenos", self.options.get("line-numbers")):
                data_start = self.options["linenos"]
            else:
                data_start = ""

        classes = " ".join([f'class="{c}"' for c in classes])
        content = "\n".join(self.content)
        result = [
            nodes.raw(
                "",
                f'<pre {data_start}><code {classes}">{content}</code></pre>',
                format="html",
            )
        ]
        # from doit.tools import set_trace; set_trace()
        return result
