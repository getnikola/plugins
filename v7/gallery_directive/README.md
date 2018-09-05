Experimental plugin to embed Nikola galleries in reStructuredText.

Usage::

    .. gallery:: demo

This should embed the gallery found in galleries/demo in your post.
Keep in mind that this is sort of a hack.

**See also:** `gallery_shortcode` plugin

Caveats:

* The styling of the displayed gallery is meant to sort-of-work
with the bootstrap-based themes

* It will **not** have the fancy rows/columns layout of the regular
gallery in bootstrap, either.

* It will look bad in most other themes. But you can customize it by
creating your own gallery_directive.tmpl. Here's the one that comes with
 the plugin for inspiration:

```html
## -*- coding: utf-8 -*-

%if post:
<p>
    ${post.text()}
</p>
%endif

<div id="gallery_container"></div>
%if photo_array:
<div class="row">
  %for image in photo_array:
    <div class="col-xs-6 col-md-3">
        <a href="${image['url']}" class="thumbnail image-reference" title="${image['title']|h}">
            <img src="${image['url_thumb']}" alt="${image['title']|h}" />
        </a>
    </div>
  %endfor
</div>

<ul class="thumbnails">
        <li>
</ul>
%endif
```

