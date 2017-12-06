What is this?
-------------

This plugin lets integrate Nikola with a Contentful site, thus allowing you to use
a web UI to create and edit posts and pages.

How to Use it
-------------

0. Setup your Contentful site using the [Nikola template](----)
1. Install the plugin using ``nikola plugin -i contentful``
3. Obtain a access token and space ID from your Contentful space and put them in a contentful.json like this:

```
{
  "SPACE_ID": 't2gxqu19qu62',
  "ACCESS_TOKEN": 'dd167cf8b111d9e17a46059d'
}
```

4. In your conf.py add ``contenful/posts`` to ``POSTS`` and ``contentful/pages`` to ``PAGES``.
5. Run ``nikola contentful``

At that point your pages and posts created in Contentful should be ready for you to use. Have fun!