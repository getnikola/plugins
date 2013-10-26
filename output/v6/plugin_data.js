var data = {
    "gallery_directive": {
        "author": "Roberto Alsina", 
        "confpy": null, 
        "description": "A directive to embed an image gallery in a reSt document", 
        "maxver": null, 
        "name": "gallery_directive", 
        "nonpyreqs": [], 
        "pyreqs": [], 
        "readme": "Experimental plugin to embed Nikola galleries in reStructuredText.\n\nUsage::\n\n    .. gallery:: demo\n\nThis should embed the gallery found in galleries/demo in your post.\nKeep in mind that this is a horrible, horrible hack.\n", 
        "tests": null, 
        "version": "0.1"
    }, 
    "graphviz": {
        "author": "Roberto Alsina", 
        "confpy": null, 
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
        "confpy": "<div class=\"code\"><pre><span class=\"c\"># Should the Hello World plugin say \u201cBYE\u201d instead?</span>\n<span class=\"n\">BYE_WORLD</span> <span class=\"o\">=</span> <span class=\"bp\">False</span>\n</pre></div>\n", 
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
    "html_roles": {
        "author": "Aru Sahni", 
        "confpy": null, 
        "description": "A collection of roles that generate html-specific tags that are not handled by vanilla docutils.", 
        "maxver": null, 
        "name": "html_roles", 
        "nonpyreqs": [], 
        "pyreqs": [], 
        "readme": "This plugin adds reStructuredText roles for several HTML tags.\n\nCurrently supported:\n\n* `del` - [Deleted text](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/del)\n* `ins` - [Inserted text](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/ins)\n* `strike` - _Deprecated_ [Strikethrough](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/strike)\n\n### Usage\n\n    .. Generates \"<ins>This text has been inserted</ins>\"\n\n    :ins:`This text has been inserted`.\n", 
        "tests": null, 
        "version": "0.1"
    }, 
    "orgmode": {
        "author": "Puneeth Chaganti", 
        "confpy": "<div class=\"code\"><pre><span class=\"c\"># NOTE: Needs additional configuration in init.el file.</span>\n\n<span class=\"c\"># Add the orgmode compiler to your COMPILERS dict.</span>\n<span class=\"n\">COMPILERS</span><span class=\"p\">[</span><span class=\"s\">&quot;orgmode&quot;</span><span class=\"p\">]</span> <span class=\"o\">=</span> <span class=\"p\">(</span><span class=\"s\">&#39;.org&#39;</span><span class=\"p\">,)</span>\n\n<span class=\"c\"># Add org files to your POSTS, PAGES</span>\n<span class=\"n\">POSTS</span> <span class=\"o\">=</span> <span class=\"n\">POSTS</span> <span class=\"o\">+</span> <span class=\"p\">((</span><span class=\"s\">&quot;posts/*.org&quot;</span><span class=\"p\">,</span> <span class=\"s\">&quot;posts&quot;</span><span class=\"p\">,</span> <span class=\"s\">&quot;post.tmpl&quot;</span><span class=\"p\">),)</span>\n<span class=\"n\">PAGES</span> <span class=\"o\">=</span> <span class=\"n\">PAGES</span> <span class=\"o\">+</span> <span class=\"p\">((</span><span class=\"s\">&quot;stories/*.org&quot;</span><span class=\"p\">,</span> <span class=\"s\">&quot;posts&quot;</span><span class=\"p\">,</span> <span class=\"s\">&quot;post.tmpl&quot;</span><span class=\"p\">),)</span>\n</pre></div>\n", 
        "description": "Compile org-mode markup into HTML using emacs.", 
        "maxver": null, 
        "name": "orgmode", 
        "nonpyreqs": [
            [
                "Emacs", 
                "https://www.gnu.org/software/emacs/"
            ], 
            [
                "Org-mode", 
                "http://orgmode.org/"
            ]
        ], 
        "pyreqs": [], 
        "readme": "This plugin implements an Emacs Org-mode based compiler for Nikola.\n\n## Setup\n\nTo start using this plugin, you will need to edit the `init.el` file\nsupplied with this plugin, and load org-mode (>=8.x).  You can add any\ncustomization variables that you wish to add, to modify the output generated\nby org-mode.\n\nYou will also need to add the orgmode compiler to your list of compilers, and\nmodify your POSTS & PAGES variables.  (See the sample conf file provided.)\n", 
        "tests": null, 
        "version": "0.1"
    }, 
    "ping": {
        "author": "Daniel Aleksandersen", 
        "confpy": "<div class=\"code\"><pre><span class=\"c\"># XML-RPC &quot;Ping&quot; services to notify of site updates. Only use after</span>\n<span class=\"c\"># production site have been successfully deployed. Excessive or &quot;false&quot;</span>\n<span class=\"c\"># pings when there are no updates will get you blacklisted with the</span>\n<span class=\"c\"># service providers.</span>\n<span class=\"c\"># List XML-RPC services (preferred) in PING_XMLRPC_SERVICES and HTTP</span>\n<span class=\"c\"># GET services (web pages) in PING_GET_SERVICES.</span>\n<span class=\"c\"># Consider adding `nikola ping` as the last entry in DEPLOY_COMMANDS.</span>\n<span class=\"n\">PING_XMLRPC_SERVICES</span> <span class=\"o\">=</span> <span class=\"p\">[</span>\n   <span class=\"s\">&quot;http://blogsearch.google.com/ping/RPC2&quot;</span><span class=\"p\">,</span>\n   <span class=\"s\">&quot;http://ping.blogs.yandex.ru/RPC2&quot;</span><span class=\"p\">,</span>\n   <span class=\"s\">&quot;http://ping.baidu.com/ping/RPC2&quot;</span><span class=\"p\">,</span>\n   <span class=\"s\">&quot;http://rpc.pingomatic.com/&quot;</span><span class=\"p\">,</span>\n<span class=\"p\">]</span>\n\n<span class=\"n\">PING_GET_SERVICES</span> <span class=\"o\">=</span> <span class=\"p\">[</span>\n   <span class=\"s\">&quot;http://www.bing.com/webmaster/ping.aspx?sitemap={0}&quot;</span><span class=\"o\">.</span><span class=\"n\">format</span><span class=\"p\">(</span><span class=\"n\">SITE_URL</span><span class=\"o\">+</span><span class=\"s\">&#39;sitemap.xml&#39;</span><span class=\"p\">),</span>\n<span class=\"p\">]</span>\n</pre></div>\n", 
        "description": "Ping services with updates to the live site", 
        "maxver": null, 
        "name": "ping", 
        "nonpyreqs": [], 
        "pyreqs": [], 
        "readme": "No README.md file available.", 
        "tests": null, 
        "version": "0.1"
    }, 
    "sphinx_roles": {
        "author": "Roberto Alsina", 
        "confpy": null, 
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
        "confpy": "<div class=\"code\"><pre><span class=\"c\"># XML-RPC &quot;Ping&quot; services to notify of site updates. Only use after</span>\n<span class=\"c\"># production site have been successfully deployed. Excessive or &quot;false&quot;</span>\n<span class=\"c\"># pings when there are no updates will get you blacklisted with the</span>\n<span class=\"c\"># service providers.</span>\n<span class=\"c\"># List XML-RPC services (preferred) in PING_XMLRPC_SERVICES and HTTP</span>\n<span class=\"c\"># GET services (web pages) in PING_GET_SERVICES.</span>\n<span class=\"c\"># Consider adding `nikola ping` as the last entry in DEPLOY_COMMANDS.</span>\n<span class=\"c\"># PING_XMLRPC_SERVICES = [</span>\n<span class=\"c\">#    &quot;http://blogsearch.google.com/ping/RPC2&quot;,</span>\n<span class=\"c\">#    &quot;http://ping.blogs.yandex.ru/RPC2&quot;,</span>\n<span class=\"c\">#    &quot;http://ping.baidu.com/ping/RPC2&quot;,</span>\n<span class=\"c\">#    &quot;http://rpc.pingomatic.com/&quot;,</span>\n<span class=\"c\"># ]</span>\n<span class=\"c\"># PING_GET_SERVICES = [</span>\n<span class=\"c\">#    &quot;http://www.bing.com/webmaster/ping.aspx?sitemap={0}&quot;.format(SITE_URL+&#39;sitemap.xml&#39;),</span>\n<span class=\"c\"># ]</span>\n</pre></div>\n", 
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