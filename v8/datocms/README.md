What is this?
-------------

This plugin lets integrate Nikola with a DatoCMS site, thus allowing you to use
a web UI to create and edit posts and pages.

How to Use it
-------------

0. Setup your Dato site using the [Nikola template](https://dashboard.datocms.com/account/sites/template?name=Nikola&siteId=4150)
1. Install the plugin using ``nikola plugin -i datocms``
2. Install the Dato CMS client inside your site using the [instructions](https://docs.datocms.com/other/basic-usage.html)

   You only need to get as far as running the dato command and getting an error about a missing ``dato.config.js``

3. Obtain a read-only token following [the same instructions](https://docs.datocms.com/other/basic-usage.html)
   and put it in a ``.env`` file (be sure not to commit it to GitHub or something like that :-)

4. In your conf.py add ``dato/posts`` to ``POSTS`` and ``dato/pages`` to ``PAGES``. **DO NOT USE YOUR REGULAR POSTS/PAGES folders, Dato deletes the contents of those folders!!!!**

5. Run ``nikola datocms``

At that point your pages and posts created in Dato should be ready for you to use. Have fun!