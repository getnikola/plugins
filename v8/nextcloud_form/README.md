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
