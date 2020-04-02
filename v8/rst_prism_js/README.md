This plugin reimplements docutil's `code` directive without pygments, using
just the suggested standard HTML5 markup like this:

```HTML
<pre>
<code class="language-python">
def f():
    pass
</code>
</pre>
```

I have tested it using prismjs.com to do the actual highlighting and it seems to work.

It implements support for most of the Sphinx extensions, such as `:emphasize-lines:` but you 
will need a prismjs with optional plugins, such as "Line Highlight" or "Line Numbers"

Sphinx's `:dedent:` and `:force:` options are ignored.
