The `latex_formula_renderer` plugin provides a static LaTeX formula rendering infrastructure, generating images which can be included in a website and do not depend on client-side rendering of formulae (as with [MathJax](https://www.mathjax.org/) and [KaTeX](https://khan.github.io/KaTeX/)). This plugin is not for end-users, but provided as a service for other plugins which can use it to not having to define their own formula-rendering functionality.

The plugin has support for
 * inline formulae, display-style formulae,
 * `align` environments (see the [AMSMath documentation](ftp://ftp.ams.org/ams/doc/amsmath/amsldoc.pdf)),
 * XY-pic diagrams (in `xymatrix` environments inside any of the previous; see the [XY-Pic user guide](http://texdoc.net/texmf-dist/doc/generic/xypic/xyguide.pdf)),
 * pstricks graphics (see [here](https://en.wikipedia.org/wiki/PSTricks) for more information), and for
 * tikzpicture graphics (see [here](https://en.wikibooks.org/wiki/LaTeX/PGF/TikZ) for more information).

It allows to generate formulae in different output formats:
 * as `.png` bitmap images;
 * as `.svg` vector graphics;
 * as compressed `.svgz` vector graphics.

The generated images do not require the user to have a certain font installed, and should render the same in all browsers and on all output devices (assuming they support the chosen graphics format and don't screw up basic things).

To see how the plugin can be used, please check out the docstring of `LaTeXFormulaRendererPlugin` in `latex_formula_renderer.py`.
