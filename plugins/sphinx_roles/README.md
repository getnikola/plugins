This plugin adds reStructuredText roles for Sphinx compatibility.

Currently supported:

* **pep:** An enhanced `:pep:` role with support for anchors, like Sphinx's
* **rfc:** An enhanced `:rfc:` role with support for anchors, like Sphinx's

The following are "semantic markup", they produce a HTML element with an extra
CSS class for styling. The description is from the Sphinx docs.

* **command:** The name of an OS-level command, such as ``rm``
* **dfn:** Mark the defining instance of a term in the text. (No index entries are generated.) [Remember Nikola has no indexes anyway]
* **kbd:** Mark a sequence of keystrokes.
* **mailheader:** The name of an RFC 822-style mail header.
* **makevar:** The name of a make variable.
* **manpage:** A reference to a Unix manual page including the section, e.g. ```:manpage:`ls(1)````
* **mimetype:** The name of a MIME type, or a component of a MIME type (the major or minor portion, taken alone).
* **newsgroup:** The name of a Usenet newsgroup.
* **program:** The name of an executable program.
* **regexp:** A regular expression. Quotes should not be included.
* **samp:** A piece of literal text, such as code. Within the contents, you can use curly braces to indicate a “variable” part.
* **file:** The name of a file or directory. Within the contents, you can use curly braces to indicate a “variable” part
* **menuselection:** Menu selections should be marked using the menuselection role. This is used to mark a complete sequence of menu selections, including selecting submenus and choosing a specific operation, or any subsequence of such a sequence. The names of individual selections should be separated by -->.
* **guilabel:** Labels presented as part of an interactive user interface should be marked using guilabel. 
