What is this?
-------------

This plugin lets syndicate Nikola content to your Medium site.


How to Use it
-------------

1. Setup a Medium account.
2. Install the plugin using ``nikola plugin -i medium``
3. Get an integration token from  your [Medium Settings Page](https://medium.com/me/settings)
4. Save the Client ID and Client Secret in ``medium.json`` like this:

```
{
  "TOKEN": "asdasdasdasd",
}
```

4. Run ``nikola medium``

At that point your posts with the "medium" metadata set to "yes" should be published. Have fun!
