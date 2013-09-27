var data = {
    "graphviz": {
        "author": "Roberto Alsina", 
        "description": "Graph directives based on Graphviz, compatible with Sphinx", 
        "maxver": null, 
        "minver": null, 
        "name": "graphviz", 
        "readme": "No README.md file available.", 
        "version": "0.1"
    }, 
    "tags": {
        "author": "Puneeth Chaganti", 
        "description": "Manage the tags for your site.", 
        "maxver": null, 
        "minver": null, 
        "name": "tags", 
        "readme": "Tags\n====\n\nTags is a plugin to manage the tags for your site.  It lets you perform bulk\noperations on your posts, to manage their tags.  It currently lets you\nperform simple operations like adding, removing, merging and sorting tags\non posts.  It can also suggest relevant tags based on the content of a\npost, leaning towards tags that already exist.\n\n**NOTE**: Tags works by modifying the headers of your posts directly.  There\nis no undo, and it is best to use it only if you have your posts under some\nform of backup.\n\nUsage\n-----\n\nThe tags command has a simple interface.  All commands take a ``-t`` option,\nto run them in test mode, that lets you see the output (if any), without\ntouching any of the files.\n\nThe usage help from the command gives details on how to use the command:\n\n    Usage:   nikola tags [-t] command [options] [arguments] [filename(s)]\n\n    Options:\n\n     -a ARG, --add=ARG         Adds a list of comma-separated tags, given a list of filenames.\n                                   $ nikola tags --add \"foo,bar\" posts/*.rst\n                               The above command will add foo and bar tags to all rst posts.\n\n     -l, --list                Lists all the tags used in the site.\n                               The tags are sorted alphabetically, by default.  Sorting can be\n                               one of 'alpha' or 'count'.\n\n     -s ARG                    Changes sorting of list; can be one of alpha or count.\n\n     --merge=ARG               Merges a list of comma-separated tags, replacing them with the last tag\n                               Requires a list of file names to be passed as arguments.\n                                   $ nikola tags --merge \"foo,bar,baz,useless\" posts/*.rst\n                               The above command will replace foo, bar, and baz with 'useless'\n                               in all rst posts.\n\n     -r ARG, --remove=ARG      Removes a list of comma-separated tags, given a list of filenames.\n                                   $ nikola tags --remove \"foo,bar\" posts/*.rst\n                               The above command will remove foo and bar tags to all rst posts.\n\n     --search=ARG              Lists all tags that match the specified search term.\n                               The tags are sorted alphabetically, by default.\n\n     -S, --sort                Sorts all the tags in the given list of posts.\n                                  $ nikola tags --sort posts/*.rst\n                               The above command will sort all tags alphabetically, in all rst\n                               posts.  This command can be run on all posts, to clean up things.\n\n     --auto-tag                Automatically tag a given set of posts.\n     -t                        Run other commands in test mode (no files are edited).\n\n\n\n\nTODO:\n-----\n\n1. Currently does not handle two post files.\n2. Not sure about the language support.  Works reasonably for English,\n   need to check.\n", 
        "version": "0.5"
    }
}