This plugin implements a [graphviz](http://www.graphviz.org/) directive similar to the one in [sphinx](http://sphinx-doc.org/ext/graphviz.html)
that lets you create graphs using [the DOT language.](http://www.graphviz.org/pdf/dotguide.pdf)

The goal is compatibility, although the implementation differs greatly.
Here's an example of [it's output](http://ralsina.me/weblog/posts/lunchtime-nikola-feature-graphviz.html)

You probably want to add something like this to your site's CSS:

```
p.graphviz { text-align: center; }
```

Incompatibilities with Sphinx:

* No support for external .dot files
* The ``:alt:`` option is ignored when using ``.. graphviz::`` (set your graph's title instead)
* There is no support for having the graph output in a separate file
* There is no support for formats other than SVG
* No way to specify the path to the dot binary
