# webmention Plugin

This is a deployment [SignalHandler](https://www.getnikola.com/extending.html#signalhandler-plugins) plugin for Nikola which looks for links in newly updated posts/pages, performs WebMention discovery on the link destination and attempts to send a [WebMention](https://indieweb.org/Webmention-developer#Protocol_Summary).

It can only *send* WebMentions, it cannot *receive* because doing so would require a dynamic stack. A service like [webmentions.io](https://webmentions.io) can be used for receiving.

----

### Configuration and Usage

If you haven't run `deploy` before, you might want to consider doing so before installing the plugin, so that it doesn't try to retroactively send mentions for all your content.

After that the plugin simply needs to be installed, copy the contents of this repo into `plugins/webmentions`

When you next make changes to your site content:

* run `nikola build`
* run `nikola deploy` (you do not need to have defined any `DEPLOY_COMMANDS` in Nikola's config)


----

### Notes

Nikola's `deploy` command does not trigger for pages/posts with a date older than the last recorded deployment, so if you are updating old pages, remember to add `Updated` to the meta-info and keep it current.


----

### Usage within posts/pages

To trigger a webmention, you simply need to include a link out to the destination as you normally would.

However, a lot of WebMention supporting software allow the *type* of mention to be adjusted based on attributes in the markup. A common way is to use [h-entry](https://indieweb.org/h-entry) markup.

----

### License

Copyright (c) 2022 B Tasker, released under [MIT License](https://choosealicense.com/licenses/mit/)
