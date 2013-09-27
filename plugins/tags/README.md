Tags
====

Tags is a plugin to manage the tags for your site.  It lets you perform bulk
operations on your posts, to manage their tags.  It currently lets you
perform simple operations like adding, removing, merging and sorting tags
on posts.  It can also suggest relevant tags based on the content of a
post, leaning towards tags that already exist.

**NOTE**: Tags works by modifying the headers of your posts directly.  There
is no undo, and it is best to use it only if you have your posts under some
form of backup.

Usage
-----

The tags command has a simple interface.  All commands take a ``-t`` option,
to run them in test mode, that lets you see the output (if any), without
touching any of the files.

The usage help from the command gives details on how to use the command:

    Usage:   nikola tags [-t] command [options] [arguments] [filename(s)]

    Options:

     -a ARG, --add=ARG         Adds a list of comma-separated tags, given a list of filenames.
                                   $ nikola tags --add "foo,bar" posts/*.rst
                               The above command will add foo and bar tags to all rst posts.

     -l, --list                Lists all the tags used in the site.
                               The tags are sorted alphabetically, by default.  Sorting can be
                               one of 'alpha' or 'count'.

     -s ARG                    Changes sorting of list; can be one of alpha or count.

     --merge=ARG               Merges a list of comma-separated tags, replacing them with the last tag
                               Requires a list of file names to be passed as arguments.
                                   $ nikola tags --merge "foo,bar,baz,useless" posts/*.rst
                               The above command will replace foo, bar, and baz with 'useless'
                               in all rst posts.

     -r ARG, --remove=ARG      Removes a list of comma-separated tags, given a list of filenames.
                                   $ nikola tags --remove "foo,bar" posts/*.rst
                               The above command will remove foo and bar tags to all rst posts.

     --search=ARG              Lists all tags that match the specified search term.
                               The tags are sorted alphabetically, by default.

     -S, --sort                Sorts all the tags in the given list of posts.
                                  $ nikola tags --sort posts/*.rst
                               The above command will sort all tags alphabetically, in all rst
                               posts.  This command can be run on all posts, to clean up things.

     --auto-tag                Automatically tag a given set of posts.
     -t                        Run other commands in test mode (no files are edited).




TODO:
-----

1. Currently does not handle two post files.
2. Not sure about the language support.  Works reasonably for English,
   need to check.
