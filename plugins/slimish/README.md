This plugin adds support for the [Slim][] template syntax via [slimish\_jinja][slimishjinja].

In order to use:

 * set your engine to `slimish` (`echo slimish > themes/$THEME/engine`)
 * create a file named `slim` in the theme directory, which contains a
   newline-separated list of Slim templates (all templates not on the list will
   be parsed by “standard” Jinja2)
 * your Slim templates must have a `.tmpl` extension

[Slim]: http://slim-lang.com/
[slimishjinja]: https://github.com/thoughtnirvana/slimish-jinja2
