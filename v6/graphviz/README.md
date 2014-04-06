This plugin implements a [graphviz](http://www.graphviz.org/) directive similar to the one in [sphinx](http://sphinx-doc.org/ext/graphviz.html)
that lets you create graphs using [the DOT language.](http://www.graphviz.org/pdf/dotguide.pdf)

The goal is compatibility, although the implementation differs greatly.
Here's an example of [it's output](http://ralsina.me/weblog/posts/lunchtime-nikola-feature-graphviz.html)

You probably want to add something like this to your site's CSS:

```
p.graphviz { text-align: center; }
```

If you have graphviz installed but you get an error about `dot` not being found,
you may need to tweak this:

```
# Path to the dot binary, if it's not in your PATH
# GRAPHVIZ_DOT = 'dot'
```

If you want to have the SVG in a separate file instead of embedded in the HTML,
you may want to change these settings in your ``conf.py``:

```
# If set to False, the graph will be in a separate file
# GRAPHVIZ_EMBED = True
# Folder where the graph will be stored
# GRAPHVIZ_OUTPUT = 'output/assets/graphviz'
# Path to use to link to the graph in the HTML output (needs trailing /)
# GRAPHVIZ_GRAPH_PATH = '/assets/graphviz/'
```


Incompatibilities with Sphinx:

* External .dot files path is considered from the current folder, which may not be what you want.
* The ``:alt:`` option is ignored when using ``.. graphviz::`` and ``GRAPHVIZ_EMBED = True`` (set your graph's title instead)
* There is no support for formats other than SVG (but why would you use any other format?)
