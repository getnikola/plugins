This plugin will allow you to compile unmodified WordPress posts using essentially the same code WordPress is using to convert posts to HTML.

Has support for shortcodes provided by plugins. Comes with a basic [code] shortcode plugin, and a basic [gallery] shortcode plugin.

To use it:

```
$ nikola plugin -i wordpress_compiler
```
Then, add `wordpress` to your `POSTS` and `PAGES` as well as your compilers dictionary in `conf.py`:
```
POSTS = (
    ("posts/*.rst", "posts", "post.tmpl"),
    ("posts/*.txt", "posts", "post.tmpl"),
    ("posts/*.wp", "posts", "post.tmpl"),
)
PAGES = (
    ("stories/*.rst", "stories", "story.tmpl"),
    ("stories/*.txt", "stories", "story.tmpl"),
    ("stories/*.wp", "stories", "story.tmpl"),
)

COMPILERS = {
    "rest": ('.txt', '.rst'),
    "wordpress": ('.wp', '.wordpress'),
    "markdown": ('.md', '.mdown', '.markdown'),
    "html": ('.html', '.htm')
}
```
Then all posts whose content is in files ending with `.wp` or `.wordpress` will be processed by the WordPress compiler plugin.