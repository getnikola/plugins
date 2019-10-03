"""Accordion directive for reStructuredText."""


import logging
from itertools import count
from collections import defaultdict

from docutils import nodes
from docutils.parsers.rst import Directive, directives
import logbook

from nikola.plugin_categories import RestExtension
from nikola.plugins.compile import rest


logger = logging.getLogger(__name__)


class Plugin(RestExtension):
    """Plugin for reST accordion directive."""

    name = "rest_accordion"

    def set_site(self, site):
        """Set Nikola site."""
        self.site = site
        directives.register_directive('accordion', Accordion)
        Accordion.site = site
        return super(Plugin, self).set_site(site)


class Accordion(Directive):
    """reST extension for inserting accordions."""

    def __init__(self, name, arguments, options, content, lineno,
                 content_offset, block_text, state, state_machine):
        super().__init__(name, arguments, options, content, lineno,
                         content_offset, block_text, state, state_machine)
        self.state_id = id(state)

    has_content = True
    optional_arguments = 1
    # the purpose of this counter stuff is to give each Accordion on a page a
    # unique number starting with one. These numbers become a part of the
    # Accordion's html id and aria controls via the template.
    counters = defaultdict(count)

    def rst2html(self, src):
        null_logger = logbook.Logger('NULL')
        null_logger.handlers = [logbook.NullHandler()]
        output, error_level, deps, _ = rest.rst2html(
            src, logger=null_logger, transforms=self.site.rst_transforms)

        return output

    def run(self):
        """Run the slides directive."""
        if len(self.content) == 0:  # pragma: no cover
            return

        if self.arguments and self.arguments[0] == 'bootstrap3':
            template_name = 'accordion_bootstrap3.tmpl'
        else:
            template_name = 'accordion_bootstrap4.tmpl'

        if self.site.invariant:  # for testing purposes
            unique_id = 'test'
        else:
            unique_id = str(next(Accordion.counters[self.state_id]) + 1)

        box_titles = []
        box_contents = []
        boxes = '\n'.join(self.content).split('\n\n\n')

        if len(boxes) == 1:
            logger.warn(
                ('Accordion directive used with only one box. '
                 'Remember to use two blank lines to separate the contents.')
            )

        for box in boxes:
            title, content = box.split('\n', 1)
            box_titles.append(self.rst2html(title))
            box_contents.append(self.rst2html(content))

        output = self.site.template_system.render_template(
            template_name,
            None,
            {
                'unique_id': unique_id,
                'box_titles': box_titles,
                'box_contents': box_contents,
            }
        )
        return [nodes.raw('', output, format='html')]
