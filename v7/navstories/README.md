This very simple plugin throws all the stories to the navigation bar.

Started as a Proof-of-concept of a ConfigPlugin.  By request on the mailing list.

Changed to map the stories to a hierachical structure in the menu
based on the permalink structure (defaults to the directory structure
of the posts).

This plugin generates menus and one level of submenus (further sub-levels are mapped to first level submenus).
WARNING: Support for submenus is theme-dependent.

The menu entries inserted by navstories are inserted after entries from `NAVIGATION_LINKS`.
Entries listed in `NAVIGATION_LINKS_POST_NAVSTORIES` are inserted after navstories entries.

Format of `NAVIGATION_LINKS_POST_NAVSTORIES` is identical to `NAVIGATION_LINKS`.

Sorting and display names in menu can be controlled for top-level entries via `NAVSTORIES_MAPPING`.

```python
NAVSTORIES_MAPPING = {
    DEFAULT_LANG: (
        # Mapping "Toplevel in permalink" to "Visible text"
        # The order is as listed here, entries not listed here are included in the end,
        # example (remove initial #):
        #("b", "Boo"),
        #("f", "Foo"),
    ),
}
NAVIGATION_LINKS_POST_NAVSTORIES = {
    # Format just as NAVIGATION_LINKS, but content included after navstories entries
}
```

To exclude a single story from the navstories meny add the following
metadata `.. hidefromnav: yes` to the story.


