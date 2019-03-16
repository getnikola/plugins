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

- Posts selected for incorporation into a feed should have `enclosure`
  metadata linking to the audio file to be used. This file needs to be
  available as part of the site source, as it will be directly
  inspected for attributes as part of the feed generation.

  .. enclosure: episode.mp3

Other per-post metadata may also be provided. For more information,
see `post.rst.sample`.
