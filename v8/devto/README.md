What is this?
-------------

This plugin can publish your Nikola content to your Devto site.


How to Use it
-------------

1. Setup a Devto account.
2. Install the plugin using ``nikola plugin -i devto``
3. Get your API token from  your [Devto Settings Page](https://docs.dev.to/api/)
4. Save the Client ID and Client Secret in ``devto.json`` like this:

```
{
  "TOKEN": "<your_devto_token>",
}
```

4. Run ``nikola devto``

At that point your posts with the "devto" metadata set to "yes" or "true" should be published.
This plugin is testing if your article was already published so don't worry for double posting.

Enjoy!
