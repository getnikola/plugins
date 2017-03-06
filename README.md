Generates podcast/netcast RSS feed from posts

## Configuration

### `POSTCAST_PATH`

Configures where postcast XML files will be generated. Default value
is `casts`.

    POSTCAST_PATH = 'casts'

### `POSTCAST_TAGS`

A sequence of tags that will be used to identifiy posts to use in
casts, with each tag generating an XML file from its tagged posts.

By default, no postcasts are generated.

    POSTCAST_TAGS = ('series1', 'series2')

### `POSTCAST_IMAGE`

A mapping of tags to images that will be used as the `itunes:image`
for the postcast. The value for tag `''` applies to all casts with no
expicit image set.

    POSTCAST_IMAGE = {
        '': 'default.jpg',
        'series1': 'series1.jpg',
        'series2': 'series2.jpg',
    }

### `POSTCAST_CATEGORIES`

A list of tuples representing `itunes:categories`.

    POSTCAST_CATEGORIES = [
        ('Category', ('Subcategory', )),
        ('Other category', ),
    ]

### `POSTCAST_EXPLICIT`

A mapping of tags to booleans that identify explicit content in each
cast. The value for tag `''` applies to all casts with no explicit
boolean set.

    POSTCAST_EXPLICIT = {
        '': None,
    }

### `TAG_PAGES_TITLES`

Used to populate each cast's title. Default title is the tag name
itself.
