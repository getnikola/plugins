This plugin allows you to cryptographically timestamp your posts and pages using
https://opentimestamps.org That means you can use the blockchain to prove that you
did write a specific thing at a specific time.

To enable it, just install the plugin, it will timestamp each and every post and page
if it's not timestamped yet.

If the contents of a post or page change, it will be timestamped again.

**IMPORTANT**

This plugin makes no effort to preserve old content or old timestamps.
If you modify your content, it's **you** are the one that has to keep
a copy of your content and the matching timestamp file. Keep in mind
that the timestamp only has a hash of the file, not the contents, so
it's not enough to prove **anything** you also need to keep a copy
of the contents you timestamped.

I suggest you put everything on git, but you do what you want. 
