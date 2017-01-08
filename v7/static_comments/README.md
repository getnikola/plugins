This plugin allows to add static comments to your theme. Static comments are taken from files `<path>/<name>.<id>.wpcomment`, where `<path>/<name>.<ext>` is the post's main file name. Such comments are for example written by the `import_wordpress` plugin when specifying the `--export-comments` argument on import.

You must use a theme which supports static comments for them to be visible (see below for instructions on how to adjust a theme).


Why use static comments?
------------------------

Static comments allow you to avoid using a dynamic (JavaScript-based) comment system. If you want users to be able to still comment things, you need to provide a form which could send the comment as an email to you, so you can create the comment files manually (or with a script).

Static comments also allow you to import a legacy WordPress blog and convert it to a completely static Nikola blog, without having to use some external service for handling the comments.


Comment files
-------------

Comment files are of the following form::

    .. id: 10
    .. approved: True
    .. author: felix
    .. author_email: felix@fontein.de
    .. author_IP: 1.2.3.4
    .. author_url: https://felix.fontein.de
    .. date_utc: 2017-01-06 11:23:55
    .. parent_id: 8
    .. wordpress_user_id: 1
    .. compiler: rest

    this is a test comment.

    the content spans the rest of the file.

Most header fields are optional. `compiler` must specify a page compiler which allows to compile a content given as a string to a string; these are currently the restructured text compiler (`rest`), the MarkDown compiler (`markdown`; only allows this in Nikola v7.8.2 or newer), and the [WordPress](https://plugins.getnikola.com/#wordpress_compiler) (`wordpress`) compiler. You can also specify `html`, in which case the comment's content will be taken as HTML without any processing.

Comments can form a hierarchy; `parent_id` must be the comment ID of the parent comment, or left away if there's no parent.


Inclusion in theme
------------------

You need a static comments aware theme to be able to actually see the comments. To modify a theme accordingly, some helper functions are provided in `templates/*/static_comment_helpers.tmpl`. They can be used as follows.

The plugin defines a variable `site_has_static_comments` with value `True`, so themes can detect the presence of static comments in general.

In templates which show the post contents (`post.tmpl` and `index.tmpl`), you can get the comments shown as follows (with jinja2 templates; adjust accordingly for mako templates)::

    [...]
    {% import 'static_comments_helper.tmpl' as static_comments with context %}
    [...]
    {% if not post.meta('nocomments') and (site_has_comments or site_has_static_comments) %}
      <div class="comments">
        <h2>{{ messages("Comments", lang) }}</h2>
        {{ static_comments.add_static_comments(post.comments, lang) }}
        [...]
      </div>
    {% endif %}
    [...]

In templates which list the posts (`list_post.tmpl`, `post_list_directive.tmpl` etc.), you can get the static comment count shown as follows::

    [...]
    {% import 'static_comments_helper.tmpl' as static_comments with context %}
    [...]
    {% if not post.meta('nocomments') and site_has_static_comments %}
      <span class="comment-count">{{ static_comments.add_static_comment_count(post.comments, lang) }}</span>
    {% endif %}
    [...]

Finally, you need to add support for some additional messages.

* `"No comments."`;
* `"{0} wrote on {1}:"` where `{0}` will be replaced by the author and `{1}` by the localized date;
* `"No comments"`;
* `"{0} comments"` where `{0}` will be replaced by a number larger than 1;
* `"{0} comment"` where `{0}` will be replaced by `1`.

Your theme might of course also print comments differently with other messages than these, by incorporating a modified version of `static_comment_helpers.tmpl`.
