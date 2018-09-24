Compiler plugin to Document Python modules using PDoc.

This module allows you to create Nikola pages based on the documentation for a python module or identifier.

Just create the page as usual:

```
nikola new_page -f pdoc
```

And as **content** in the page, put a module name, for example, this will create a page with the documentation for the csv module:

```
csv
```

You can also use a module and an identifier. To document the excel identifier in the csv module:

```
csv excel
```

This is still rather raw, the output doesn't look great, the JS interactions are broken, and CSS is lacking, but it's a start.

[More information about PDoc](https://github.com/mitmproxy/pdoc)



