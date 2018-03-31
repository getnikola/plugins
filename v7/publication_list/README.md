# Publication List

A Nikola plugin to easily manage publication list.

This plugin provides a directive `publication_list`, which reads a BibTeX file
and display the references in them on the web page.

The publications are displayed in the following way. All publications are sorted
by year in reverse order, i.e., recent publication first. Publications in the
same year are grouped together with a year subtitle. Within the same year,
publications are sorted by order they appear in the BibTeX file. Finally, each
publication is formatted with the designated style.

## Options

The `publication-list` directive accepts multiple options.

* `:bibtex_dir:` indicates the directory where the bibtex file of each
  publication is generated. If empty, no bibtex file will be created for each
  publication. The default is `bibtex`.

* `:detail_page_dir:` indicates the directory where the details pages of the
  publications are stored. If empty, no details page will be created. The
  default is `papers`.

* `:highlight_author:` indicates the author to highlight. Usually this is the
  owner of the website. This can be a list of names separated by “;” if there are several
  optional names.

In the BibTeX file entries, the following fields have special meanings.

* `abstract` is the abstract of the paper. If it is present, the abstract will
  be available in the details page.
* `fulltext` is the URL to the full text of the paper (usually a PDF file). If
  it is present, a "full text" link will be shown below the publication and the
  PDF file will be embedded in the details page.
* Fields starting with `customlink` will add custom links below the publication.
  For example, `customlinkslides` will add a link `[slides]` to the URL of the
  value of the field.

If you need math support, please add the following to your `EXTRA_HEAD_DATA`
option in your `conf.py` file, then every math equation surrounded by `\(` and
`\)`, e.g., the ones in the abstracts and titles, will be rendered properly.

    r'<script type="text/javascript" src="https://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML"> </script>'

## Example

A simple example:

    Publications
    ------------

    .. publication_list:: my-publications.bib
       :style: unsrt
       :highlight_author: Nikola Tesla

where `my-publications.bib` contains:

    @article{a2015,
        title = {One Article in 2015},
        author = {Nikola Tesla},
        year = 2015,
        journal = {Great Journal},
        volume = 1,
        pages = {1--10},
        fulltext = {/pdf/a2015.pdf}
    }

    @book{b2010,
        title = {One Book in 2010},
        author = {Isaac Newton and Nikola Tesla},
        year = 2010,
        isbn = {000-0000000000},
        publisher = {Nikola Tesla Publishing Group},
        fulltext = {http://example.org/b2010.pdf}
    }

    @inproceedings{p2015,
        title = {One Conference in 2015},
        booktitle = {Nikola Tesla Conference},
        author = {Nikola Tesla},
        year = 2015
    }

If you have multiple bibtex files, you can specify them in one line, separated
by spaces. For example:

    ... publication_list:: my-novels.bib my-research-papers.bib my-collections.bib

Live examples:

- http://www.shudan.me/
- https://bishesh.github.io/publications/

## Customize Details Pages

You can also customize details pages. To do that, simply create files named
`publicationlist_label_after_abstract.html` or
`publicationlist_label_after_fulltext.html` in your template directory (usually
named `templates`). The contents in these files will be inserted into the
details page of the paper with that BibTeX label. For example, for a paper with
a BibTeX label `a2015`, you can create files
`publicationlist_a2015_after_abstract.html` and/or
`publicationlist_a2015_after_fulltext.html` to customize its details page.

## Screenshot

![publication-list screenshot](http://plugins.getnikola.com/__data__/publication-list-screenshot.png)

[list of styles]: https://bitbucket.org/pybtex-devs/pybtex/src/master/pybtex/style/formatting/
[Pybtex]: http://pybtex.org
