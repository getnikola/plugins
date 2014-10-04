[CommonMark][spec] (formerly known as *Common Markdown* and *Standard Markdown*
before renaming due to licensing disputes) strives to be a strongly specified
and highly compatible implementation of [Markdown][md], the markup language
created by John Gruber in 2004.

The `commonmark` Nikola plugin is a post compiler, using the [CommonMark][pypi]
Python package to compile Markdown code.  The package is a pure-Python port of
`stmd.js`, a reference JavaScript implementation of CommonMark.

This plugin is an alternative to the `markdown` plugin (which is using
`python-markdown`), `pandoc` (using Pandoc, which handles many more input
formats), and `misaka` (yet another custom Markdown implementation).  All the
plugins can be used on one site, provided that file extensions differ.

This plugin **does not** support MarkdownExtension plugins.  They are only
compatible with the `markdown` plugin and `python-markdown`.

[pypi]: https://pypi.python.org/pypi/CommonMark
[spec]: http://commonmark.org/
[md]: http://daringfireball.net/projects/markdown/
