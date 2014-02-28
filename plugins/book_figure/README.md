Plugin to embed book link.

Usage::

    .. book_figure:: title
    	:class:
    	:url:
    	:author:
        :isbn_13:
        :isbn_10:
        :asin:
        :image_url:
        
        Your review.

This should embed the book link.

### Examples

This reStructuredText document:

```ReST

	.. book_figure:: Get Nikola
        :class: book-figure
        :url: http://getnikola.com/
        :author: Roberto Alsina
        :isbn_13: 1234567890123
        :isbn_10: 1234567890
        :asin: B001234567
        :image_url: http://getnikola.com/galleries/demo/tesla2_lg.jpg

        Your review.
```

will result in:

```html

    <div class="book-figure">
        <div class="book-figure-media">
        	<a class="book-figure-image" href="http://getnikola.com/" target="_blank">
        		<img src="http://getnikola.com/galleries/demo/tesla2_lg.jpg" alt="Get Nikola" />
        	</a>
        </div>
        <div class="book-figure-content">
        	<a class="book-figure-title" href="http://getnikola.com/" target="_blank">Get Nikola</a>
        	<p class="book-figure-author">by Roberto Alsina</p>
        	<table class="book-figure-book-number">
        		<tbody>
			        <tr><th>ISBN-13:</th><td>1234567890123</td></tr>
			        <tr><th>ISBN-10:</th><td>1234567890</td></tr>
			        <tr><th>ASIN:</th><td>B001234567</td></tr>
        		</tbody>
        	</table>
        	<div class="book-figure-review">
        		<p>Your review.</p>
        	</div>
        </div>
    </div>
```

Screenshot: 
![book-figure screenshot](book-figure-screenshot.png "book-figure screenshot")
