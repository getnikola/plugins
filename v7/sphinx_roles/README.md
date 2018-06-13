This plugin adds reStructuredText roles and directives for Sphinx compatibility.

Currently supported:

* **pep:** An enhanced `:pep:` role with support for anchors, like Sphinx's
* **ref:** Cross references for arbitrary locations (see [the sphinx docs](http://sphinx-doc.org/markup/inline.html#role-ref)). Limited to links inside a single document.
* **rfc:** An enhanced `:rfc:` role with support for anchors, like Sphinx's
* **term:** Reference to a term in the glossary
* **option:** Reference to a option defined using the option directive
* **eq:** Reference to a equation defined in a math directive's label option.
* **math:** A Math directive that supports a :label: option like Sphinx's

The following are "semantic markup", they produce a HTML element with an extra
CSS class for styling. The description is from the Sphinx docs.

* **abbr**: abbreviations with explanations
* **command:** The name of an OS-level command, such as ``rm``
* **dfn:** Mark the defining instance of a term in the text. (No index entries are generated.) [Remember Nikola has no indexes anyway]
* **kbd:** Mark a sequence of keystrokes.
* **mailheader:** The name of an RFC 822-style mail header.
* **makevar:** The name of a make variable.
* **manpage:** A reference to a Unix manual page including the section.
* **mimetype:** The name of a MIME type, or a component of a MIME type (the major or minor portion, taken alone).
* **newsgroup:** The name of a Usenet newsgroup.
* **program:** The name of an executable program.
* **regexp:** A regular expression. Quotes should not be included.
* **samp:** A piece of literal text, such as code. Within the contents, you can use curly braces to indicate a “variable” part.
* **file:** The name of a file or directory. Within the contents, you can use curly braces to indicate a “variable” part
* **menuselection:** Menu selections should be marked using the menuselection role. This is used to mark a complete sequence of menu selections, including selecting submenus and choosing a specific operation, or any subsequence of such a sequence. The names of individual selections should be separated by -->.
* **guilabel:** Labels presented as part of an interactive user interface should be marked using guilabel.

This plugin also implementes Sphinx's [extlinks extension](http://sphinx-doc.org/latest/ext/extlinks.html)
which lets you create "shortcuts" to URLs that follow a pattern. You need to declare the patterns
in `conf.py`:

```
EXTLINKS = {'issue': ('https://bitbucket.org/birkenfeld/sphinx/issue/%s',
                      'issue ')}
```

Which will create this link [issue 123](https://bitbucket.org/birkenfeld/sphinx/issue/123) out of this:

```
:issue:`123`
```

For more details see [the sphinx docs for extlinks.](http://sphinx-doc.org/latest/ext/extlinks.html)

It also implements the following [paragraph-level markup from Sphinx](http://sphinx-doc.org/markup/para.html):

* **versionadded**
* **versionchanged**
* **deprecated**
* **centered**
* **hlist** -- Needs the user to define a hlist class in CSS that removes table borders to look good.
* **seealso** -- Needs the user to define a seealso class in CSS to change the look of the admonition.

And finally, there is limited support for:

* **glossary** -- Partially implemented: the term role only works in the same file as the glossary, and it doesn't support multiple terms per definition.
* **option** -- Flaky, links from the option role don't work across files.
