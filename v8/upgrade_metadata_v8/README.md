Nikola Metadata Upgrade (v7 to v8)
==================================

This is a plugin to upgrade metadata in `.meta` files from the old format
(without descriptions) to the new reST-esque format. It only applies to users
with two-file posts (`.meta` files alongside text) in the older format (up to 7
lines of text without any descriptions), used by Nikola before v8.0.0. If this
is the case on your site, **you will be warned** by `nikola build` — otherwise,
don’t install this plugin (it won’t do a thing anyway and will only waste disk
space and load time).

The plugin adds the `nikola upgrade_metadata_v8` command. Remove the plugin
manually after the upgrade.
