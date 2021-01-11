This plugin renders [PlantUML](https://plantuml.com/) in Markdown files.

# Requirements

* Python >= 3.6 (we use `markdown>=3.3.0` which requires it)

# Usage

Diagrams are rendered as inline SVGs.

A code listing can be rendered at either side of the diagram or on its own.

~~~text
SVG diagram
-----------
  
```plantuml
A -> B : foo
```

Diagram with listing on the left
--------------------------------

```{ .plantuml listing+svg }
A -> B : foo
```

Diagram with listing on the right
---------------------------------

```{ .plantuml svg+listing }
A -> B : foo
```

Just the listing
----------------

```{ .plantuml listing }
A -> B : foo
```
~~~

All [fenced code options](https://python-markdown.github.io/extensions/fenced_code_blocks/) are available e.g.

~~~text
HTML IDs (for top level div & each listing line)
------------------------------------------------

```{ .plantuml svg+listing #my_id }
A -> B : foo
```

Line Numbering
--------------

```{ .plantuml listing #my_id linenos=true }
A -> B : foo
```

Line Highlighting
-----------------
```{ .plantuml listing hl_lines="1 2" }
A -> B : foo
B -> A : bar
A -> B : baz
```

~~~

A common prefix can be specified for all subsequent diagrams in a page.
The most common use for this is probably page specific theming.  e.g.

~~~text

```plantuml-prefix
' This block specifies the "prefix" and does not render as HTML
skinparam ArrowFontName Courier
skinparam ArrowFontColor Red
```

```plantuml
A -> B : This arrow uses red Courier font
```

```plantuml
A -> B : So does this one
```

The prefix can be changed and following diagrams will use the new (possibly empty) prefix:

```plantuml-prefix
```

```plantuml
A -> B : This arrow uses the default style
```
~~~

# Known Issues

* Code listings do not have pretty syntax highlighting because there is no
  [Pygments Lexer](https://pygments.org/docs/lexers/) for PlantUML.
  