# postcast plugin for Nikola

Generates podcast/netcast RSS feeds from posts. It is originally based
on the speechsynthesizednetcast copyright © 2013–2014 Daniel
Aleksandersen and others.

**LIVE DEMO:** https://civilfritz.net/casts/gameolder.xml


## Why use this plugin?

Nikola is, among other things, a site generator capable of creating
aggregation feeds from a collection of posts. These posts can be
associated with metadata. By adding `enclosure` and other metadata to
a post, these posts effectively become entries in a podcast-style rss
feed suitable for publication with popular podcast platforms and
subscription by popular podcast applications.


## Usage

- `casts` directory is the location in `output` where your cast feeds
  will be generated. You can change this by setting `POSTCAST_PATH`.

      POSTCAST_PATH = 'casts'

- By default, no postcast feeds are generated; one feed will be
  generated for each entry in the `POSTCASTS` list.

      POSTCASTS = ['mycast']

- Each cast feed can be associated with a Nikola category. Only posts
  in that category will be incorporated into the feed.

      POSTCAST_CATEGORY = {
          'mycast': 'cat_mycast',
      }

- Each cast feed can further (or in stead) be associated with a list
  of tags. Only posts with *all* of the tags in the list will be
  incorporated into the feed.

      POSTCAST_TAGS = {
          'mycast': ['mycast-episode'],
      }

Other configuration options are available. For more information, see
`conf.py.sample`.


## Peta fields

- **category** - the post category is used to select posts for the
    feed

- **tag** - post tags are used to select posts for the feed

- **author** - the post author is used to identify the author of the
    episode in the feed

- **itunes_author** - an explicit author for the episode can be
    specified if it differs from the post author

- **itunes_summary** - an explicit summary can be provided for the
    episode; otherwise, the body of the post will be used

- **itunes_image** - episode art

- **enclosure** - the audio file (usually .mp3 or .ogg) to be
    distributed

- **itunes_duration** - the real-time length of the audio file; used
    to provide this information to applications before the file has
    been downloaded

- **itunes_subtitle** - a short description that provides general
    information about the episode

- **itunes_explicit** - a boolean expressing whether the episode
    contains explicit content; overrides POSTCAST_ITUNES_EXPLICIT

For more information, see `post.rst.sample`.
