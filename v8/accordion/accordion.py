"""Slides directive for reStructuredText."""


import uuid
import logging

from docutils import nodes
import logbook
from nikola.plugin_categories import RestExtension
from docutils.parsers.rst import Directive, directives
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

    has_content = True

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

        if self.site.invariant:  # for testing purposes
            hex_uuid4 = 'fixedvaluethatisnotauuid'
        else:
            hex_uuid4 = uuid.uuid4().hex

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
            'accordion.tmpl',
            None,
            {
                'hex_uuid4': hex_uuid4,
                'box_titles': box_titles,
                'box_contents': box_contents,
            }
        )
        return [nodes.raw('', output, format='html')]
