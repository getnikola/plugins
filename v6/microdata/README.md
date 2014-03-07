This plugin adds microdata semantic markups in reStructuredText for Nikola static blog generator. The original author is Axel Haustant (noirbizarre). This code is fork from https://github.com/noirbizarre/pelican-microdata. The standalone package will be at https://github.com/ivanteoh/nikola-microdata

Currently supported in general:

* `itemscope`
* `itemprop`

### Usage

```ReST

    .. itemscope:: <Schema type>
        :tag: element type (default: div)

        Nested content


    :itemprop:`Displayed test <itemprop name>`
```

### Examples

This reStructuredText document:

```ReST

    .. itemscope: Person
        :tag: p

        My name is :itemprop:`Bob Smith <name>`
        but people call me :itemprop:`Smithy <nickanme>`.
        Here is my home page:
        :itemprop:`www.exemple.com <url:http://www.example.com>`
        I live in Albuquerque, NM and work as an :itemprop:`engineer <title>`
        at :itemprop:`ACME Corp <affiliation>`.
```

will result in:

```html

    <p itemscope itemtype="http://data-vocabulary.org/Person">
        My name is <span itemprop="name">Bob Smith</span>
        but people call me <span itemprop="nickname">Smithy</span>.
        Here is my home page:
        <a href="http://www.example.com" itemprop="url">www.example.com</a>
        I live in Albuquerque, NM and work as an <span itemprop="title">engineer</span>
        at <span itemprop="affiliation">ACME Corp</span>.
    </p>
```
