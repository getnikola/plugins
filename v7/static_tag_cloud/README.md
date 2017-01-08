This plugin renders configurable static tag clouds. These tag clouds can also be for different taxonomies (for example categories or sections), and there can be different ones for the same taxonomy (for example a large and small variant; the large to include in the tag overview page, and the small one to include in the sidebar).

The generated HTML fragment and CSS file, one per language, must be somehow included in the rest of the blog. This can be done by using JavaScript to dynamically load the files, or by using tools like [File Tree Subs](https://github.com/felixfontein/filetreesubs/).

See `conf.py.sample` for an example of how to configure some tag clouds.
