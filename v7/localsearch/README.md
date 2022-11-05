If you don't want to depend on Google or DuckDuckGo to implement search for you,
or just want it to work even if you are offline, enable this plugin and the
search will be performed client side. It uses [Tipue Search](https://web.archive.org/web/20200703134724/https://tipue.com/search/) as its engine.

In ordrer to set up Tipue, you will need:

 * the sample config from `conf.py.sample` and a page set up to render `localsearch.tmpl` (which you may customize) —
   an example is in `search-EXAMPLE.html`
 * or the alternate sample config from `conf.py.sample.alt`, which uses a modal
   and does not need another page
 * jQuery on the search page; you might need to modify the templates if your theme doesn’t already include it

For more information about how to customize it and use it, please refer to the [Tipue Search docs](https://web.archive.org/web/20200703134724/https://tipue.com/search/).

Tipue is under an MIT license (see MIT-LICENSE.txt)
