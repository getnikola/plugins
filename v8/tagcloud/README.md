This plugin generates data in JSON format, for use by tag clouds. This used to be in core before v8 as an optional feature.

Data is saved into `output/assets/js/tag_cloud_data.json`. Sample:

```json
{"blog": [1, "/categories/blog/", {"posts": [{"date": "03/30/2012", "isodate": "2012-03-30T23:00:00-03:00", "title": "Welcome to Nikola", "url": "/posts/welcome-to-nikola/"}]}]}
````

(Note: this plugin does *not* provide any front-end features, you’ll need to
take care of that yourself.)
