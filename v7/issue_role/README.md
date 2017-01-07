This plugin adds a new reStructuredText role `:issue:`, which automatically
creates URLs pointing to the respective issue on the tracker defined in
`ISSUE_URL`.

Currently, the URL needs to be set in the GLOBAL_CONTEXT in conf.py

`{issue}` will be replaced with the text provided to the `:issue:`
reStructuredText role.

Example:

When you set `ISSUE_URL` to `http://tracker.yoursite.com/issue/{issue}`
using ``:issue:`FOO-123` `` in your post will be converted to:
`<a href="http://tracker.yoursite.com/issue/FOO-123">FOO-123</a>` in the
resulting HTML page.
