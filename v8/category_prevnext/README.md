This plugin changes the previous/next links below the posts to reflect the category index instead of the global index.
This way, the categories of a blog behave more like independent subblogs.

There is no configuration needed, but i recommend to replace the blog index by a static page to avoid confusing readers.
This can be archived by setting INDEX\_PATH to some subdirectory, adding pages output to the root directory

    PAGES = (
      ("pages/*.md", "", "page.tmpl"),
    )

and creating a corresponding pages/index.md file.

This plugin replaces `section_prevnext` from v7.
