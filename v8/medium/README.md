# What is this

-------------

This plugin lets syndicate Nikola content to your Medium site.

## How to Use it

-------------

1. Setup a Medium account.
2. Install the plugin using ``nikola plugin -i medium``
3. Get an integration token from  your [Medium Settings Page](https://medium.com/me/settings)
4. Save the Client ID and Client Secret in ``medium.json`` like this:

``` json
{
  "TOKEN": "asdasdasdasd",
}
```

5. Run ``nikola medium``

At that point your posts with the "medium" metadata set to "yes" should be published.
Any article that does not have "medium" metadata, or is set to "false" will be skipped.

**Be aware that if you use the command again after a short period of time it might post duplicate article, medium is taking a bit of time before updating the list of your posted articles that I compare from to avoid that.**
