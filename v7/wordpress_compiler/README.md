This plugin will allow you to compile unmodified WordPress posts using essentially the same code WordPress is using to convert posts to HTML.

Has support for shortcodes provided by plugins. Comes with [code] shortcode plugin.

To use it:

```
$ nikola plugin -i wordpress_compiler
```
Then, add `wordpress` to your compilers in `conf.py`:
```
COMPILERS = {
        "rest": ('.txt', '.rst'),
        "wordpress": ('.wp', '.wordpress'),
        "markdown": ('.md', '.mdown', '.markdown'),
        "html": ('.html', '.htm')
        }
```
Then all posts whose content is in files ending with `.wp` will be processed by the WordPress compiler plugin.