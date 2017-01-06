This plugin renders a sidebar ``output/sidebar-LANG.inc`` defined by a template ``sidebar.tmpl``. The sidebar can contain the most recent posts, all categories, all tags, the archives, all sections, and other taxonomies and arbitrary other content. The packaged ``sidebar.tmpl`` and ``sidebar-helper.tmpl`` shows how this information can be shown.

The generated include file, one per language, must be somehow included in the rest of the blog. This can be done by using JavaScript to dynamically include the file, or by using tools like `File Tree Subs <https://github.com/felixfontein/filetreesubs/>`__.

The number of most recent posts can be changed by defining ``SIDEBAR_MAXIMAL_POST_COUNT = number`` in the Nikola configuration.
