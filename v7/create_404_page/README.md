This plugin creates a 404 page (`404.html`) which can be used as a 404 error page for your web server (i.e. it doesn't use relative links).

To use this, you need a template `404.tmpl`. The plugin provides simple templates both for Mako and Jinja, but you can easily adjust them to your needs. The default templates assume that the strings `'Page not found'` and `'The page you are trying to access does not exist. Please use your browser\'s "back" button to return to the previous page.'` are translated. If your blog uses another language than English, you need to translate these strings yourself and provide the translations in your theme's `messages_XX.py` files. Or (for simple one-language blogs) simply adjust the strings in `404.tmpl`.

Note that this plugin requires version 7.8.1 of Nikola. If that version isn't released yet, you need the current GitHub `master` branch.
