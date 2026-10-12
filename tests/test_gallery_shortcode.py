import lxml.html
from pytest import mark

from v8.gallery_shortcode.gallery_shortcode import get_photo_array

PHOTOS = [
    {'url': 'tesla_tower1_lg.jpg', 'url_thumb': 'tesla_tower1_lg.thumbnail.jpg', 'title': 'Tesla tower1 lg',
     'size': {'w': 1024, 'h': 768}},
    {'url': 'tesla; "lightning".jpg', 'url_thumb': 'tesla; "lightning".thumbnail.jpg', 'title': 'A; "quoted" title',
     'size': {'w': 800, 'h': 600}},
]

NOSCRIPT = """
<noscript>
<ul class="thumbnails">
    <li><a href="tesla_tower1_lg.jpg" class="thumbnail image-reference" title="Tesla tower1 lg">
        <img src="tesla_tower1_lg.thumbnail.jpg" alt="Tesla tower1 lg" loading="lazy" /></a>
    <li><a href="tesla; &quot;lightning&quot;.jpg" class="thumbnail image-reference" title="A; &quot;quoted&quot; title">
        <img src="tesla; &quot;lightning&quot;.thumbnail.jpg" alt="A; &quot;quoted&quot; title" loading="lazy" /></a>
</ul>
</noscript>
"""


def gallery_page(body):
    return lxml.html.fromstring('<html><body><div id="gallery_container"></div>{}</body></html>'.format(body))


# The photo list as the different kinds of gallery pages contain it
JSON_DATA_BLOCK = NOSCRIPT + """
<script id="gallery-data" type="application/json" data-thumbnail-size="400">
[{"url": "tesla_tower1_lg.jpg", "url_thumb": "tesla_tower1_lg.thumbnail.jpg", "title": "Tesla tower1 lg", "size": {"w": 1024, "h": 768}},
 {"url": "tesla; \\"lightning\\".jpg", "url_thumb": "tesla; \\"lightning\\".thumbnail.jpg", "title": "A; \\"quoted\\" title", "size": {"w": 800, "h": 600}}]
</script>
<script src="/assets/js/gallery-init.js"></script>
"""

INLINE_SCRIPT = NOSCRIPT + """
<script src="/assets/js/justified-layout.min.js"></script>
<script src="/assets/js/gallery.min.js"></script>
<script>
var jsonContent = [{"url": "tesla_tower1_lg.jpg", "url_thumb": "tesla_tower1_lg.thumbnail.jpg", "title": "Tesla tower1 lg", "size": {"w": 1024, "h": 768}}, {"url": "tesla; \\"lightning\\".jpg", "url_thumb": "tesla; \\"lightning\\".thumbnail.jpg", "title": "A; \\"quoted\\" title", "size": {"w": 800, "h": 600}}];
var thumbnailSize = 400;
renderGallery(jsonContent, thumbnailSize);
window.addEventListener('resize', function(){renderGallery(jsonContent, thumbnailSize)});
</script>
"""


@mark.parametrize('body', [JSON_DATA_BLOCK, INLINE_SCRIPT], ids=['json-data-block', 'inline-script'])
def test_full_photo_list(body):
    assert get_photo_array(gallery_page(body)) == PHOTOS


def test_noscript_links_only():
    # Themes whose base.tmpl drops the gallery's script block
    expected = [{k: v for k, v in photo.items() if k != 'size'} for photo in PHOTOS]
    assert get_photo_array(gallery_page(NOSCRIPT)) == expected


def test_image_links_outside_noscript_are_ignored():
    body = '<p><a class="image-reference" href="other.jpg"><img src="other.thumbnail.jpg"></a></p>'
    assert get_photo_array(gallery_page(body)) is None


def test_no_photos():
    assert get_photo_array(gallery_page('<p>An empty gallery</p>')) is None
