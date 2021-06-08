#!/usr/bin/env python3
# Generate category pages
# TODO in Nikola v8: rename Compiler → PageCompiler (#2543)
categories = ['Command', 'CommentSystem', 'CompilerExtension', 'ConfigPlugin', 'LateTask', 'Compiler', 'PostScanner', 'ShortcodePlugin', 'SignalHandler', 'Task', 'TaskMultiplier', 'TemplateSystem', 'MetadataExtractor']
template = """\
.. title: {0}
.. slug: {0}
.. date: 1970-01-01 00:00:00 UTC
.. category: category_page

.. post-list::
   :sort: slug_sortable
   :categories: {0}
   :post_type: pages
   :template: plugin_list.tmpl
"""

for category in categories:
    with open(category + '.rst', 'w', encoding='utf-8') as fh:
        fh.write(template.format(category))
        print(category)
