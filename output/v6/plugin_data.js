var data = {
    "graphviz": {
        "author": "Roberto Alsina", 
        "description": "Graph directives based on Graphviz, compatible with Sphinx", 
        "maxver": null, 
        "minver": null, 
        "name": "graphviz", 
        "nonpyreqs": [
            [
                "Graphviz", 
                "http://www.graphviz.org/"
            ]
        ], 
        "pyreqs": [], 
        "readme": "This plugin implements a [graphviz](http://www.graphviz.org/) directive similar to the one in [sphinx](http://sphinx-doc.org/ext/graphviz.html)\nthat lets you create graphs using [the DOT language.](http://www.graphviz.org/pdf/dotguide.pdf)\n\nThe goal is compatibility, although the implementation differs greatly.\nHere's an example of [it's output](http://ralsina.me/weblog/posts/lunchtime-nikola-feature-graphviz.html)\n\nYou probably want to add something like this to your site's CSS:\n\n```\np.graphviz { text-align: center; }\n```\n\nIncompatibilities with Sphinx:\n\n* No support for external .dot files\n* The ``:alt:`` option is ignored when using ``.. graphviz::`` (set your graph's title instead)\n* There is no support for having the graph output in a separate file\n* There is no support for formats other than SVG\n* No way to specify the path to the dot binary\n", 
        "tests": null, 
        "version": "0.1"
    }, 
    "sphinx_roles": {
        "author": "Roberto Alsina", 
        "description": "A set of reStructuredText roles for Sphinx compatibility", 
        "maxver": null, 
        "minver": null, 
        "name": "sphinx_roles", 
        "nonpyreqs": [], 
        "pyreqs": [], 
        "readme": "This plugin adds reStructuredText roles for Sphinx compatibility.\n\nCurrently supported:\n\n**pep:** An enhanced `:pep:` role with support for anchors, like Sphinx's\n**rfc:** An enhanced `:rfc:` role with support for anchors, like Sphinx's\n**abbr:** An abbreviation. If the role content contains a parenthesized explanation, it will be treated specially: it will be shown in a tool-tip in HTML.<pre>:abbr:`LIFO (last-in, first-out)`.</pre>\n\nThe following are \"semantic markup\", they produce a HTML element with an extra\nCSS class for styling. The description is from the Sphinx docs.\n\n* **command:** The name of an OS-level command, such as ``rm``\n* **dfn:** Mark the defining instance of a term in the text. (No index entries are generated.) [Remember Nikola has no indexes anyway]\n* **kbd:** Mark a sequence of keystrokes.\n* **mailheader:** The name of an RFC 822-style mail header.\n* **makevar:** The name of a make variable.\n* **manpage:** A reference to a Unix manual page including the section, e.g. ```:manpage:`ls(1)````\n* **mimetype:** The name of a MIME type, or a component of a MIME type (the major or minor portion, taken alone).\n* **newsgroup:** The name of a Usenet newsgroup.\n* **program:** The name of an executable program.\n* **regexp:** A regular expression. Quotes should not be included.\n", 
        "tests": null, 
        "version": "0.1"
    }, 
    "tags": {
        "author": "Puneeth Chaganti", 
        "description": "Manage the tags for your site.", 
        "maxver": null, 
        "minver": null, 
        "name": "tags", 
        "nonpyreqs": [], 
        "pyreqs": [], 
        "readme": "Tags\n====\n\nTags is a plugin to manage the tags for your site.  It lets you perform bulk\noperations on your posts, to manage their tags.  It currently lets you\nperform simple operations like adding, removing, merging and sorting tags\non posts.  It can also suggest relevant tags based on the content of a\npost, leaning towards tags that already exist.\n\n**NOTE**: Tags works by modifying the headers of your posts directly.  There\nis no undo, and it is best to use it only if you have your posts under some\nform of backup.\n\nUsage\n-----\n\nThe tags command has a simple interface.  All commands take a ``-n, --dry-run``\noption, to do a dry run, that lets you see the output (if any),\nwithout\ntouching any of the files.\n\nThe usage help from the command gives details on how to use the command:\n\n    Usage:   nikola tags [-n|--dry-run] command [options] [arguments] [filename(s)]\n\n    Options:\n\n     -a ARG, --add=ARG         Adds a list of comma-separated tags, given a list of filenames.\n                                   $ nikola tags --add \"foo,bar\" posts/*.rst\n                               The above command will add foo and bar tags to all rst posts.\n\n     -l, --list                Lists all the tags used in the site.\n                               The tags are sorted alphabetically, by default.  Sorting can be\n                               one of 'alpha' or 'count'.\n\n     -s ARG                    Changes sorting of list; can be one of alpha or count.\n\n     --merge=ARG               Merges a list of comma-separated tags, replacing them with the last tag\n                               Requires a list of file names to be passed as arguments.\n                                   $ nikola tags --merge \"foo,bar,baz,useless\" posts/*.rst\n                               The above command will replace foo, bar, and baz with 'useless'\n                               in all rst posts.\n\n     -r ARG, --remove=ARG      Removes a list of comma-separated tags, given a list of filenames.\n                                   $ nikola tags --remove \"foo,bar\" posts/*.rst\n                               The above command will remove foo and bar tags to all rst posts.\n\n     --search=ARG              Lists all tags that match the specified search term.\n                               The tags are sorted alphabetically, by default.\n\n     -S, --sort                Sorts all the tags in the given list of posts.\n                                  $ nikola tags --sort posts/*.rst\n                               The above command will sort all tags alphabetically, in all rst\n                               posts.  This command can be run on all posts, to clean up things.\n\n     --auto-tag                Automatically tag a given set of posts.\n     -n, --dry-run             Dry run (no files are edited).\n\n\n\n\nTODO:\n-----\n\n1. Currently does not handle two post files.\n2. Not sure about the language support.  Works reasonably for English,\n   need to check.\n", 
        "tests": "test_command_tags", 
        "version": "0.5"
    }
}