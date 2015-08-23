WIP Plugin to import arbitrary web pages.

Usage:

```
nikola import_page http://en.wikipedia.org/wiki/Information_extraction
```

That will produce a information-extraction-wikipedia-the-free-encyclopedia.html that you can edit
and move into your stories/ folder.

You will need something like this in conf.py:

```
PAGES = (
    ("stories/*.html", "stories", "story.tmpl"),
)
```
