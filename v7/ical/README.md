**NOTE:** This plugin needs a Nikola release greater than 7.7.12. If you can't see such a release, then it still requires unreleased master from GitHub.


This plugin implements a shortcode to display calendar information.

The calendar information is provided in iCalendar format, either via an
external file, or embedded in your document.

Example with external file:

```
{{% calendar file=my_event.ical %}}
```

Example with embedded calendar:

```
{{% calendar %}}
BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//hacksw/handcal//NONSGML v1.0//EN
BEGIN:VEVENT
UID:uid1@example.com
DTSTAMP:19970714T170000Z
ORGANIZER;CN=John Doe:MAILTO:john.doe@example.com
DTSTART:19970714T170000Z
DTEND:19970715T035959Z
SUMMARY:Bastille Day Party
END:VEVENT
END:VCALENDAR
{{% /calendar %}}

```

The plugin provides simple templates both for Mako and Jinja, but if you want to use
a different template, just use the ``template`` argument (it will be loaded from the theme
or from ``templates/``:

```
{{% calendar file=my_event.ical template=my_fancy_template.tmpl %}}
```
