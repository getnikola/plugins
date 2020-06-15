This plugin converts Nikola into the equivalent of [Planet](http://www.planetplanet.org/)
a feed aggregator. It requires [PeeWee](https://github.com/coleifer/peewee) and
[Feedparser](http://code.google.com/p/feedparser/) to work.

It has a configuration option: `PLANETOID_REFRESH` which is the number of minutes
before retrying a feed (defaults to 60).

You need to create a ``feeds`` file containing the data of which feeds you want to
aggregate. The format is very simple:

```
   # Roberto Alsina
   http://feeds2.feedburner.com/PostsInLateralOpinionAboutPython
   Roberto Alsina
```

* Lines that start with ``#`` are comments and ignored.
* Lines that start with http are feed URLs.
* URL lines have to be followed by the "real name" of the feed.

After all that is in place, just run ``nikola build`` and you'll get
a planet.
If you run ``nikola build`` for the first time you need to actually issue
the command three times until the planet is build.

There is a special theme for the planets called `planetoid`. To use
this, run `nikola theme -i planetoid` and set `THEME` in your `conf.py` to
`'planetoid'`.  This is special in the case that it redirects users to the
original URL of the post when they try to open a post.
