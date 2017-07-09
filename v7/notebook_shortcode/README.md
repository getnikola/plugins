This plugin inserts a Jupyter/IPython notebook into a post using shortcode. This is useful, for example, when
adapting an existing notebook into a post with additional markup.

Usage:

```
{{% raw %}}{{% notebook path/to/notebook.ipynb %}}{{% /raw %}}
```

Note: `ipynb` must be enabled and configured (COMPILERS, POSTS/PAGES) for CSS to appear properly. If you are using math
in your notebook, make sure to add the `mathjax` tag to your post.
