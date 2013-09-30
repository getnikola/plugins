var data = {
    "graphviz": {
        "author": "Roberto Alsina", 
        "description": "Graph directives based on Graphviz, compatible with Sphinx", 
        "maxver": null, 
        "name": "graphviz", 
        "nonpyreqs": [
            [
                "Graphviz", 
                "http://www.graphviz.org/"
            ]
        ], 
        "pyreqs": [], 
        "readme": "This plugin implements a [graphviz](http://www.graphviz.org/) directive similar to the one in [sphinx](http://sphinx-doc.org/ext/graphviz.html)\nthat lets you create graphs using [the DOT language.](http://www.graphviz.org/pdf/dotguide.pdf)\n\nThe goal is compatibility, although the implementation differs greatly.\nHere's an example of [it's output](http://ralsina.me/weblog/posts/lunchtime-nikola-feature-graphviz.html)\n\nYou probably want to add something like this to your site's CSS:\n\n```\np.graphviz { text-align: center; }\n```\n\nIf you have graphviz installed but you get an error about `dot` not being found,\nyou may need to tweak this:\n\n```\n# Path to the dot binary, if it's not in your PATH\n# GRAPHVIZ_DOT = 'dot'\n```\n\nIf you want to have the SVG in a separate file instead of embedded in the HTML,\nyou may want to change these settings in your ``conf.py``:\n\n```\n# If set to False, the graph will be in a separate file\n# GRAPHVIZ_EMBED = True\n# Folder where the graph will be stored\n# GRAPHVIZ_OUTPUT = 'output/assets/graphviz'\n# Path to use to link to the graph in the HTML output (needs trailing /)\n# GRAPHVIZ_GRAPH_PATH = '/assets/graphviz/'\n```\n\n\nIncompatibilities with Sphinx:\n\n* External .dot files path is considered from the current folder, which may not be what you want.\n* The ``:alt:`` option is ignored when using ``.. graphviz::`` and ``GRAPHVIZ_EMBED = True`` (set your graph's title instead)\n* There is no support for formats other than SVG (but why would you use any other format?)\n", 
        "tests": null, 
        "version": "0.1"
    }, 
    "helloworld": {
        "author": "Roberto Alsina", 
        "description": "Dummy plugin that says hi", 
        "maxver": "9001.0.0", 
        "minver": "6.0.0", 
        "name": "helloworld", 
        "nonpyreqs": [], 
        "pyreqs": [
            "Nikola\n", 
            "doit\n", 
            "logbook\n"
        ], 
        "readme": "This is a simple plugin you can use as a basis for your own. It does nothing interesting:\n\n* It creates a task for Nikola\n* The task prints a notice saying \"Hello World\"\n* The task is always considered out of date, so it always runs, unless you set `BYE_WORLD=True` in conf.py\n", 
        "tests": "test_helloworld", 
        "version": "0.1"
    }, 
    "sphinx_roles": {
        "author": "Roberto Alsina", 
        "description": "A set of reStructuredText roles for Sphinx compatibility", 
        "maxver": null, 
        "name": "sphinx_roles", 
        "nonpyreqs": [], 
        "pyreqs": [], 
        "readme": "This plugin adds reStructuredText roles for Sphinx compatibility.\n\nCurrently supported:\n\n* **pep:** An enhanced `:pep:` role with support for anchors, like Sphinx's\n* **rfc:** An enhanced `:rfc:` role with support for anchors, like Sphinx's\n\nThe following are \"semantic markup\", they produce a HTML element with an extra\nCSS class for styling. The description is from the Sphinx docs.\n\n* **command:** The name of an OS-level command, such as ``rm``\n* **dfn:** Mark the defining instance of a term in the text. (No index entries are generated.) [Remember Nikola has no indexes anyway]\n* **kbd:** Mark a sequence of keystrokes.\n* **mailheader:** The name of an RFC 822-style mail header.\n* **makevar:** The name of a make variable.\n* **manpage:** A reference to a Unix manual page including the section.\n* **mimetype:** The name of a MIME type, or a component of a MIME type (the major or minor portion, taken alone).\n* **newsgroup:** The name of a Usenet newsgroup.\n* **program:** The name of an executable program.\n* **regexp:** A regular expression. Quotes should not be included.\n* **samp:** A piece of literal text, such as code. Within the contents, you can use curly braces to indicate a \u201cvariable\u201d part.\n* **file:** The name of a file or directory. Within the contents, you can use curly braces to indicate a \u201cvariable\u201d part\n* **menuselection:** Menu selections should be marked using the menuselection role. This is used to mark a complete sequence of menu selections, including selecting submenus and choosing a specific operation, or any subsequence of such a sequence. The names of individual selections should be separated by -->.\n* **guilabel:** Labels presented as part of an interactive user interface should be marked using guilabel.\n\nThis plugin also implementes Sphinx's [extlinks extension](http://sphinx-doc.org/latest/ext/extlinks.html)\nwhich lets you create \"shortcuts\" to URLs that follow a pattern. You need to declare the patterns\nin `conf.py`:\n\n```\nEXTLINKS = {'issue': ('https://bitbucket.org/birkenfeld/sphinx/issue/%s',\n                      'issue ')}\n```\n\nWhich will create this link [issue 123](https://bitbucket.org/birkenfeld/sphinx/issue/123) out of this:\n\n```\n:issue:`123`\n```\n\nFor more details see [the sphinx docs for extlinks.](http://sphinx-doc.org/latest/ext/extlinks.html)\n", 
        "tests": null, 
        "version": "0.1"
    }, 
    "tags": {
        "author": "Puneeth Chaganti", 
        "description": "Manage the tags for your site.", 
        "maxver": null, 
        "name": "tags", 
        "nonpyreqs": [], 
        "pyreqs": [], 
        "readme": "Tags\n====\n\nTags is a plugin to manage the tags for your site.  It lets you perform bulk\noperations on your posts, to manage their tags.  It currently lets you\nperform simple operations like adding, removing, merging and sorting tags\non posts.  It can also suggest relevant tags based on the content of a\npost, leaning towards tags that already exist.\n\n**NOTE**: Tags works by modifying the headers of your posts directly.  There\nis no undo, and it is best to use it only if you have your posts under some\nform of backup.\n\nUsage\n-----\n\nThe tags command has a simple interface.  All commands take a ``-n, --dry-run``\noption, to do a dry run, that lets you see the output (if any),\nwithout\ntouching any of the files.\n\nThe usage help from the command gives details on how to use the command:\n\n    Usage:   nikola tags [-n|--dry-run] command [options] [arguments] [filename(s)]\n\n    Options:\n\n     -a ARG, --add=ARG         Adds a list of comma-separated tags, given a list of filenames.\n                                   $ nikola tags --add \"foo,bar\" posts/*.rst\n                               The above command will add foo and bar tags to all rst posts.\n\n     -l, --list                Lists all the tags used in the site.\n                               The tags are sorted alphabetically, by default.  Sorting can be\n                               one of 'alpha' or 'count'.\n\n     -s ARG                    Changes sorting of list; can be one of alpha or count.\n\n     --merge=ARG               Merges a list of comma-separated tags, replacing them with the last tag\n                               Requires a list of file names to be passed as arguments.\n                                   $ nikola tags --merge \"foo,bar,baz,useless\" posts/*.rst\n                               The above command will replace foo, bar, and baz with 'useless'\n                               in all rst posts.\n\n     -r ARG, --remove=ARG      Removes a list of comma-separated tags, given a list of filenames.\n                                   $ nikola tags --remove \"foo,bar\" posts/*.rst\n                               The above command will remove foo and bar tags to all rst posts.\n\n     --search=ARG              Lists all tags that match the specified search term.\n                               The tags are sorted alphabetically, by default.\n\n     -S, --sort                Sorts all the tags in the given list of posts.\n                                  $ nikola tags --sort posts/*.rst\n                               The above command will sort all tags alphabetically, in all rst\n                               posts.  This command can be run on all posts, to clean up things.\n\n     --auto-tag                Automatically tag a given set of posts.\n     -n, --dry-run             Dry run (no files are edited).\n\n\n\n\nTODO:\n-----\n\n1. Currently does not handle two post files.\n2. Not sure about the language support.  Works reasonably for English,\n   need to check.\n", 
        "tests": "test_command_tags", 
        "version": "0.5"
    }
}