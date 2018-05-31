# -*- coding: utf-8 -*-

# Copyright © 2016 Roberto Alsina and others

# This plugin is based on the Pelican ical plugin
# available at https://github.com/getpelican/pelican-plugins/tree/master/ical
#
# This plugin is licensed under the
# GNU AFFERO GENERAL PUBLIC LICENSE Version 3
# according to the license guidelines from the Pelican plugin repo
#
# Original code is written by:
#
# Julien Ortet: https://github.com/cozo
# Justin Mayer: https://github.com/justinmayer
# calfzhou: https://github.com/calfzhou

from __future__ import print_function

import icalendar as ical

from nikola.plugin_categories import ShortcodePlugin
from nikola.utils import LocaleBorg


class CalendarPlugin(ShortcodePlugin):
    """Calendar shortcode."""
    name = "ical"

    doc_purpose = "Display ical calendars"
    doc_description = "Format and display ical calendars."
    logger = None
    cmd_options = []

    def set_site(self, site):
        super(CalendarPlugin, self).set_site(site)
        self.site.register_shortcode('calendar', self.handler)

    def handler(self, site=None, data=None, lang=None, file=None, template=None, post=None):
        if not template:
            template = 'calendar.tmpl'
        deps = self.site.template_system.template_deps(template)

        if file is not None:
            with open(file, 'rb') as inf:
                data = inf.read()
            deps.append(file)
        cal = ical.Calendar.from_ical(data)

        events = []
        for element in cal.walk():
            eventdict = {}
            if element.name == "VEVENT":
                if element.get('summary') is not None:
                    eventdict['summary'] = element.get('summary')
                if element.get('description') is not None:
                    eventdict['description'] = element.get('description')
                if element.get('url') is not None:
                    eventdict['url'] = element.get('url')
                if element.get('dtstart') is not None:
                    eventdict['dtstart'] = element.get('dtstart').dt
                if element.get('dtend') is not None:
                    eventdict['dtend'] = element.get('dtend').dt
                events.append(eventdict)

        output = self.site.render_template(
            template,
            None,
            {
                'events': events,
                'lang': LocaleBorg().current_lang,
            })

        return output, deps
