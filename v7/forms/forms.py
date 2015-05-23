# -*- coding: utf-8 -*-
# This file is public domain according to its author, Brian Hsu

import uuid

from docutils.parsers.rst import Directive, directives
from docutils import nodes

from nikola.plugin_categories import RestExtension


class Plugin(RestExtension):

    name = "rest_form"

    def set_site(self, site):
        self.site = site
        directives.register_directive('form', AlpacaForms)
        return super(Plugin, self).set_site(site)


class AlpacaForms(Directive):
    """ Embed AlpacaForm form

        Usage:

          .. form::

             [Alpaca form description as JSON]

          .. form::
             :file: formdescription.json


    """

    option_spec = {'file': directives.unchanged}
    has_content = True

    def run(self):
        formname = 'form_'+uuid.uuid4().hex
        fname = self.options.get('file')
        if fname is None:
            data = '\n'.join(self.content)
        else:
            with open(fname, 'rb') as fd:
                data = fd.read()
        return [nodes.raw('', '''
            <div id={formname} class="alpacaform"></div> <script type="text/javascript"> {formname}_data={data};</script>'''.format(formname=formname, data=data), format='html')]
