What is this?
-------------

This plugin lets syndicate Nikola content to your Medium site.

KNOWN BUGS
----------

Because of Medium's API limitations if you run this twice your posts will be published twice.
So, use with care?

How to Use it
-------------

0. Setup a Medium account.
1. Install the plugin using ``nikola plugin -i medium``
3. Get an integration token from  your [Medium Settings Page](https://medium.com/me/settings)
4. Save the Client ID and Client Secret in ``medium.json`` like this:

```
{
  "TOKEN": "asdasdasdasd",
}
```

4. Run ``nikola medium``

At that point your posts with the "medium" metadata set to "yes" should be published. Have fun!
