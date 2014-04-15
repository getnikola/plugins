ReStructuredText extension to show files side-by-side.

Sample usage:

```
.. diff::
   :left: path/to/version-1
   :right: path/to/version-2
```

You will probably want to add something like this to your ``custom.css``

```
.diff_add {background-color: lightgreen; display: block; font-family: monospace;}
.diff_sub {background-color: #ffa0a0; display: block; font-family: monospace;}
td.diff_header {padding-left:6px; padding-right:6px; text-align:right;}
table.diff {white-space: pre;}
```
