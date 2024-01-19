# Podcast RSS Feed Generator
Used for publishing RSS feeds for an arbitrary set of audio formats

# Usage
Add the following options to your `config.py`
```
# List of feed types you want to create
PODCAST_FEEDS = ['mp3', 'ogg']

# Base URL for where the files are hosted
POD_BASE_URL="https://archive.org/download/urandom-00X/urandom-00X."

# Adding the 'enclosure' and 'enclosure_length' metadata to the posts, to get added to the feeds
ADDITIONAL_METADATA = {}
for feed in PODCAST_FEEDS:
    ADDITIONAL_METADATA[feed + "_enclosure"] = POD_BASE_URL + feed
    ADDITIONAL_METADATA[feed + "_enclosure_length"] = feed + "_length"
```


# Other notes
Even if you're not creating multiple feeds, many podcatchers require enclosures to have an accurate length. Please consider setting it.
