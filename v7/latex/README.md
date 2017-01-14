This plugin allows to write posts and pages in a LaTeX-like syntax.

For Python before 3.4, you need to install the [`enum34` library](https://pypi.python.org/pypi/enum34). From Python 3.4 on, it is part of the language.


Formulae
--------

There are two available formulae backends:

 * one based on the [`latex_formula_renderer` plugin](https://plugins.getnikola.com/v7/latex_formula_renderer/);
 * one based on [MathJax](https://www.mathjax.org/).

The first plugin allows special features the second doesn't:

 * `align` environments (see the [AMSMath documentation](ftp://ftp.ams.org/ams/doc/amsmath/amsldoc.pdf));
 * XY-pic diagrams (see the [XY-Pic user guide](http://texdoc.net/texmf-dist/doc/generic/xypic/xyguide.pdf));
 * PSTricks graphics (see [here](https://en.wikipedia.org/wiki/PSTricks) for more information);
 * TikZ pictures (see [here](https://en.wikibooks.org/wiki/LaTeX/PGF/TikZ) for more information).

You need an installed LaTeX distribution for this to work, with some extra tools. See the `latex_formula_renderer` plugin for details.


Required Translations
---------------------

You need to add the following translations to your theme if you use theorem environments:
``` .py
MESSAGES = {
    'math_thm_name': 'Theorem',
    'math_prop_name': 'Proposition',
    'math_cor_name': 'Corollary',
    'math_lemma_name': 'Lemma',
    'math_def_name': 'Definition',
    'math_defs_name': 'Definitions',
    'math_proof_name': 'Proof',
    'math_example_name': 'Example',
    'math_examples_name': 'Examples',
    'math_remark_name': 'Remark',
    'math_remarks_name': 'Remarks',
}
```
