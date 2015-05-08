This plug-in generates a /index.json file containing the same posts
as /index.html. Intended to be used in JavaScripts. For example to
promote the most recent posts at the bottom of older posts.

By default, the JSON file will include:
    {
        <JS Date object>: {
            "title": <post-title>,
            "iri": <relative-link-to-post>
        },
    }

Optionally, it can be expanded to include thumbnails or descriptions:
    { <JS Date object>: {
        "title": <post-title>, "iri": <post-relative-link>,
        "desc": <post-meta-description>,
        "img": <post-meta-thumbnail>
    }, }

Posts are sorted by their post.meta.date as JavaScript dates.

Pro tip: Set a sensible cache header for the JSON file.
