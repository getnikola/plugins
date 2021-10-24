An implementation of the [JSON Feed](https://jsonfeed.org/) specification (version 1.1).

Supported:

* archives (`/archives/2017/feed.json` — only if archives are indexes)
* blog index (`/feed.json`)
* author pages (`/authors/john-doe-feed.json`)
* categories (`/categories/cat_foo-feed.json`)
* tags (`/categories/bar-feed.json`)

Unsupported:

* galleries (requires some changes to Nikola core)

Sample output
-------------

```json
{
    "version": "https://jsonfeed.org/version/1.1",
    "user_comment": "This feed allows you to read the posts from this site in any feed reader that supports the JSON Feed format. To add this feed to your reader, copy the following URL — https://example.com/feed.json — and add it your reader.",
    "title": "Demo Site",
    "home_page_url": "https://example.com/",
    "feed_url": "https://example.com/feed.json",
    "description": "This is a demo site for Nikola.",
    "authors": [{
        "name": "Your Name"
    }],
    "author": {
        "name": "Your Name"
    },
    "items": [
        {
            "id": "https://example.com/posts/welcome-to-nikola.html",
            "url": "/posts/welcome-to-nikola.html",
            "title": "Welcome to Nikola",
            "date_published": "2012-03-30T23:00:00-03:00",
            "authors": [{
                "name": "Roberto Alsina",
                "url": "/authors/roberto-alsina.html"
            }],
            "author": {
                "name": "Roberto Alsina",
                "url": "/authors/roberto-alsina.html"
            },
            "tags": [
                "blog",
                "demo",
                "nikola",
                "python"
            ],
            "external_url": "https://getnikola.com/",
            "content_html": "…omitted for brevity…"
        }
    ]
}
```
