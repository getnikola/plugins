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