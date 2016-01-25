# Publication List

A Nikola plugin to easily manage publication list.

This plugin provides a directive `publication-list`, which reads a BibTeX file
and display the references in them on the web page. The `publication-list`
directive accepts one option `:style:`, which is the style of the bibliography.
All available styles are provided by [Pybtex][]. You can see the
[list of styles][] in the Pybtex repository. The default style is `unsrt`.

The publications are displayed in the following way. All publications are sorted
by year in reverse order, i.e., recent publication first. Publications in the
same year are grouped together with a year subtitle. Within the same year,
publications are sorted by order they appear in the BibTeX file. Finally, each
publication is formatted with the designated style.

## Example

A simple example:

    Publications
    ------------

    .. publication_list:: my-publication.bib
       :style: unsrt

where `my-publication.bib` contains:

    @article{a2015,
        title = {One Article in 2015},
        author = {Nikola Tesla},
        year = 2015,
        journal = {Great Journal},
        volume = 1,
        page = {1--10}
    }

    @book{b2010,
        title = {One Book in 2010},
        author = {Nikola Tesla and Isaac Newton},
        year = 2010,
        isbn = {000-0000000000},
        publisher = {Nikola Tesla Publishing Group}
    }

    @inproceedings{p2015,
        title = {One Conference in 2015},
        booktitle = {Nikola Tesla Conference},
        author = {Nikola Tesla},
        year = 2015
    }

## Screenshot

![publication-list screenshot](http://plugins.getnikola.com/__data__/publication-list-screenshot.png)

[list of styles]: https://bitbucket.org/pybtex-devs/pybtex/src/eb1b9f24e22f1802eaf609c320212d10b3b949a5/pybtex/style/formatting/?at=master
[Pybtex]: http://pybtex.org
