Nikola Metadata Upgrade
=======================

This is a plugin to upgrade metadata in `.meta` files from the old format
(without descriptions) to the new reST-esque format. It only applies to users
with two-file posts (`.meta` files alongside text) in the older format (up to 7
lines of text without any descriptions), used by Nikola before v7.0.0. If you
need to use this plugin, **you will be warned** by `nikola build` — otherwise,
there is no need to install it.
