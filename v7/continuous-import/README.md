The continuous import plugin lets Nikola work as a hub for the different
ways in which you put content out on the Internet. For example, you may
post book reviews in GoodReads, or movie reviews at a different site,
or have a Tumblr, or post links at Reddit.

Using continuous import you can have that content presented also in your own
site, making it the authoritative source for all things you write, and giving
you a backup in case those sites ever disappear.

TODO: explain better how it works

TODO: do more templates for more services

TODO: add a generic default template that "sort of works"

```
# This is a list of feeds whose contents will be imported as posts into
# your blog via the "nikola continuous_import" command.

FEEDS = {
    'goodreads': {
        'url': 'https://www.goodreads.com/review/list_rss/1512608?key=N4VCVq54T-sxk8wx4UMRYIZKMVqQpbZN4gdYG22R4dv04LM2&shelf=read',
        'template': 'goodreads.tmpl',
        'output_folder': 'posts/goodreads',
        'format': 'html',
        'lang': 'en',
        'metadata': {
            'title': 'title',
            'date': 'published',
            'tags': 'books, goodreads',
        }
    }
}
```
