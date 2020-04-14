Plugin to support tagging pages, and creating lists of 
page tags and of pages for a given tag.

In general, very similar to the regular tag support except where it makes no sense:

* No RSS/Atom feeds (pages don't necessarily have dates)
* No equivalent for `TAG_PAGES_ARE_INDEXES` for same reason

There is no translation message for "Pages tagged [whatever]" so if you use any language
other than English you will need to configure `TAGGED_PAGES_TITLES` to get nice
output.

