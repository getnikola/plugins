This plugin changes the previous/next links below the posts to reflect the section index instead of the global index.
This way, the sections of a blog behave more like independent subblogs.

There is no configuration needed, but i recommend to replace the blog index by a static page to avoid confusing readers.
This can be archived by setting INDEX\\_PATH to some subdirectory and adding a

    PAGES = (
      ("pages/*.md", "", "story.tmpl"),
   	)

and a corresponding index.md file.

Depends on taxonomies introduced in Nikola 7.8.2 so be sure to use a recent version.
