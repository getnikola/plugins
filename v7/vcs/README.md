This **EXPERIMENTAL** plugin tries to make it easy to keep your site in a version control system.

**REMEMBER**, this is a first iteration, it's probably buggy, so be careful, and only use it
if you are experienced with your VCS, ok?

How to use it:

1. Choose your favourite VCS between git, bzr, subversion, mercurial.
2. Initialize the repo in your site (for example: ``git init .``)
3. Install this plugin: ``nikola plugin -i vcs``
4. Run ``nikola vcs``
5. Check what happened (for example: ``git status`` and ``git log``)
6. Use your site as usual, creating posts, adding stuff or removing it
7. GOTO 4.

What it should do:

1. Add a lot of stuff to the repo:

   * All your posts
   * All your pages
   * All your galleries' images
   * All your listings
   * All your static files
   * Your themes
   * Your plugins
   * Your conf.py

2. Remove stuff if you removed it
3. Commit stuff if you changed it

What it should **NOT** do:

1. Lose your data
2. Push it anywhere (yet)
3. Manage your output (consider ``github_deploy`` would not like it!)

Please report anything missing, or any ideas on how to improve this, where you want this to go
by [filing issues](https://github.com/getnikola/plugins/issues).
