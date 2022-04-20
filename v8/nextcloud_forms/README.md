This plugin embeds a Nextcloud Forms formular in a static site.
It provides a mechanism for the static HTML site to embed a form and to collect
and store the user data.

The form specification is loaded at build time from the Nextcloud using the
public form link. The HTML form is then build according to the extracted JSON
form specification.

When the submit button is pressed a simple JS function collects the form data
and sends it to the Nextcloud server using the public API.

## Requirements and setup

For this plugin to work a Nextcloud with the Forms App is needed.

Create a form and make it public. Copy the public link and pass it as the
`link` parameter to the nextcloud_forms shortcut:

```
{{% nextcloud_forms link="https://nextcloud_url/index.php/apps/forms/..." %}}
Success Text
{{% /nextcloud_forms %}}
```

The `Success Text` is shown after the form is successfully sent to the server.

## Heads up

Nextcloud Forms public API is not handling CORS requests correctly, especially
the preflight checks. This leads to the XmlHTTPRequest failing with a CORS
error and the browser not submitting the data.

At the moment there are two open feature requests at Nextcloud Server and
Nextcloud Forms that should fix these issues:

- https://github.com/nextcloud/server/pull/31698
- https://github.com/nextcloud/forms/pull/1139

Until these are merged into upstream, at least the changes to Nextcloud Forms
have to be applied manually to the Nextcloud installation.
