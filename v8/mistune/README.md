This plugin is an alternative to the `markdown` plugin (which is using
`python-markdown`), `pandoc` (using Pandoc, which handles many more input
formats), and `misaka` (yet another custom Markdown implementation).  All the
plugins can be used on one site, provided that file extensions differ.

This one is based on [mistune](https://github.com/lepture/mistune) which is 
impresively fast (only 50% slower than misaka) while being pure python.

For context: CommonMark is 2.5x slower than Mistune, and Python Markdown is
a mind-boggling 60x slower.

This plugin **does not** support MarkdownExtension plugins.  They are only
compatible with the `markdown` plugin and `python-markdown`.

Research on using Mistune extensions with Nikola is needed.
