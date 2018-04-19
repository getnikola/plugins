
This plugin converts filepaths from breadcrumbs into more pretty
breadcrumbs based on metadata information defined in the source
file.

For example, if file `test/index.rst` contains

```
.. crumb: This is a test
```

the breadcrumb generated would be `This is a test` instead of `test`.

By default, the plugin looks for the metadata tag `crumb` but this
can be changed via `PRETTY_BREADCRUMBS_TAG`.

