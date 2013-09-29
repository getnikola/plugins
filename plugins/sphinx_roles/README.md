This plugin adds reStructuredText roles for Sphinx compatibility.

Currently supported:

**pep:** An enhanced `:pep:` role with support for anchors, like Sphinx's
**rfc:** An enhanced `:rfc:` role with support for anchors, like Sphinx's

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
