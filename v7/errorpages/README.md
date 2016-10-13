This plugin allows to create HTTP error pages (`404.html`, `403.html`, etc.) which can be used as error pages for your web server (for 404, 403, etc. errors). These pages never use relative links, no matter whether you use relative links for the rest of your blog or not.

To use this, you need a template `XXX.tmpl` for every [HTTP status code](https://en.wikipedia.org/wiki/List_of_HTTP_status_codes) `XXX`. The plugin provides simple templates `404.tmpl` both for Mako and Jinja, but you can easily adjust them to your needs. These default templates assume that the strings `'Page not found'` and `'The page you are trying to access does not exist. Please use your browser\'s "back" button to return to the previous page.'` are translated. If your blog uses another language than English, you need to translate these strings yourself and provide the translations in your theme's `messages_XX.py` files. Or (for simple one-language blogs) simply adjust the strings in `XXX.tmpl`.

To tell the plugin which error pages to create, add `CREATE_HTTP_ERROR_PAGES` to your `conf.py`. This must be a list of error codes, like
~~~
# Create 404 error page
CREATE_HTTP_ERROR_PAGES = [404]
~~~
for a 404 error page, and
~~~
# Create 401, 403 and 404 error pages
CREATE_HTTP_ERROR_PAGES = [401, 403, 404]
~~~
for both 403 and 404 error pages. Note that you need to provide a `403.tmpl` template for the latter example.

You also need to configure your web server accordingly. You can find documentation on how to do that for common webservers here: [Apache](https://httpd.apache.org/docs/2.4/custom-error.html), [Nginx](http://nginx.org/en/docs/http/ngx_http_core_module.html#error_page). It will work out of the box on [GitHub Pages](https://help.github.com/articles/creating-a-custom-404-page-for-your-github-pages-site/).

Note that this plugin requires version 7.8.1 of Nikola.
