This very simple plugin throws all the stories to the navigation bar.

Started as a Proof-of-concept of a ConfigPlugin.  By request on the mailing list.

Changed to map the stories/pages to a hierachical structure in the menu
based on the permalink structure (defaults to the directory structure
of the posts).

This plugin generates menus and one level of submenus (further sub-levels are mapped to first level submenus).
WARNING: Support for submenus is theme-dependent.

The menu entries inserted by navstories are inserted after entries from `NAVIGATION_LINKS`.
Entries listed in `NAVIGATION_LINKS_POST_NAVSTORIES` are inserted after navstories entries.

Format of `NAVIGATION_LINKS_POST_NAVSTORIES` is identical to `NAVIGATION_LINKS`.

To include stories in the menu the permalink for the story must start with one of the strings listed in
`NAVSTORIES_PATHS`, other stories should be ignored by this pluging.

Sorting and display names in menu can be controlled for top-level entries via `NAVSTORIES_MAPPING`.

```python
# Paths (permalink) that should be processed by navstories plugin (path starting with /<variable>/, <variable> can contain /, e.g.: stories/b
NAVSTORIES_PATHS = {
    DEFAULT_LANG: (
        'pages',
        'stories',
    ),
}
# Mapping "Toplevel in permalink" to "Visible text"
# The order is as listed here, entries not listed here are included in the end, with the top level of the permalink as text
NAVSTORIES_MAPPING = {
    DEFAULT_LANG: (
        # example (remove initial #):
        #("b", "Boo"),
        #("f", "Foo"),
    ),
}
# Indention for each level deeper in a submenu, than the highest level in that submenu, the submenu is flat, so it is only the menu text there are indented
NAVSTORIES_SUBMENU_INDENTION = '* '
# Static menu after dynamic navstories menu entries
# Format just as NAVIGATION_LINKS, but content included after navstories entries
NAVIGATION_LINKS_POST_NAVSTORIES = {
}
```

To exclude a single story from the navstories meny add the following
metadata `.. hidefromnav: yes` to the story.


