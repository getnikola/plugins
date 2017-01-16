This plugin allows to write posts and pages in a subset of LaTeX. This makes it possible to use the same `.tex` file both as input to this page compiler and as an include for a real LaTeX document.

For Python before 3.4, you need to install the [`enum34` library](https://pypi.python.org/pypi/enum34). From Python 3.4 on, it is part of the language.


Supported LaTeX subset
======================

The posts should contain what usually is contained between `\begin{document}` and `\end{document}` in a LaTeX document.

The following LaTeX or LaTeX-similar constructs can be used:

* Simple formatting such as `\textbf{...}`, `\textit{...}`, `\texttt{...}` and `\emph{...}`.
* `\begin{center} ... \end{center}` can be used for centered text.
* `\begin{blockquote} ... \end{blockquote}` can be used for block quotes.
* Formulae:
  * Everything of the form `$...$`, `\( ... \)` for inline formulae.
  * Everything of the form `$$...$$`, `\[ ... \]` for display-style formulae.
  * `\begin{align} ... \end{align}` and `\begin{align*} ... \end{align*}` for
    aligned formulae from the AMSMath package. Note that no equation numbers will be used in HTML output, and that you cannot use `\label{...}` and `\ref{...}` with `\begin{align}` environments.
  * Everything of the form `\begin{pstricks}{...} ... \end{pstricks}`.
  * Everything of the form `\begin{tikzpicture}[...] ... \end{tikzpicture}`.
  * There is a special environment for lists of formulae which can be rearranged in multiple columns: `\begin{formulalist} \formula{$1+1$} \formula{$f(x)$} ... \end{formulalist}`
    The `\begin{formulalist}` can have an optional argument which indicates the number of columns. This is currently not used.

  Please note that the use of align-style formulae, PSTricks images and TikZ pictures requires the [`latex_formula_renderer` plugin](https://plugins.getnikola.com/v7/latex_formula_renderer/); see below for more information.

* Enumerations:
  * Ordered enumerations with `\begin{enumerate} \item ... \end{enumerate}`.
  * Unordered enumerations with `\begin{itemize} \item ... \end{itemize}`.
* Source code:
  * Inline with `\code{lang}{...}` or `\code{lang}|...|`, where `lang` specifies the language and `|` can also be any other character than `{` and `[` which marks both the beginning and the end of the inline code.
  * Block with `\begin{codelisting}{lang} ... \end{codelisting}`.

  The language field is currently passed unprocessed to pygments.
* Controls like `\\` and `\newpar`.
* Section headers like `\chapter{...}`, `\section{...}`, `\subsection{...}` and `subsubsection{...}`.
* Theorem environments:
  * `\begin{definition} ... \end{definition}`;
  * `\begin{definitions} ... \end{definitions}`;
  * `\begin{lemma} ... \end{lemma}`;
  * `\begin{proposition} ... \end{proposition}`;
  * `\begin{theorem} ... \end{theorem}`;
  * `\begin{corollary} ... \end{corollary}`;
  * `\begin{example} ... \end{example}`;
  * `\begin{examples} ... \end{examples}`;
  * `\begin{remark} ... \end{remark}`;
  * `\begin{remarks} ... \end{remarks}`;
  * `\begin{proof} ... \end{proof}`.

  To add a QED sign at the end of an environment, use `\qed` inside the environment. This is done automatically for `proof` environments.

  Also, the environments have an optional title argument: `\begin{theorem}[Fermat's Last Theorem] ... \end{theorem}`
* Labels `\label{...}` are recognized in some contexts (section headers and theorem environments) and can be refered to with `\ref{...}` or `\ref[Text]{label}`.
* URLs can be inserted with `\url{...}` and hyperlinks with `\href{url}{text}`.
* Short texts in foreign languages can be marked with `\foreignlanguage{language}{text}`.
* Arbitrary unicode symbols can be inserted with `\symbol{...}`, where the decimal representation must be used.
* `\noindent` and `\setlength{...}{...}` are ignored.
* Images can be inserted with `\includegraphics{filename}` or `\includegraphics[...]{filename}`. The optional argument is a comma-separated list of `key=value` pairs, where we support the keys `width`, `height`, and `alt` (for the `<img alt=""` argument in HTML). The width and height values can be of the following forms:
  * If the unit ends with `\textwidth` resp. `\textheight`, the value before will be interpreted as a fractional value (or 1 if there is nothing before) and converted to a percent value in HTML output.
  * If the unit ends with `cm`, it will be converted to `em` in HTML output.
  * Otherwise, the unit will be expected to be a unit-less number and will be taken as pixel size in HTML output.
* Tables can be set with `\begin{tabular}{...} ... \end{tabular}`. Both `\hline` and `\cline{...}` are supported, and the argument of `\begin{tabular}` can consist out of `|`, `l`, `r` and `c`.
* Pictures can be grouped with `\begin{picturegroup} \picture{title}{commands} ... \end{picturegroup}`. The `commands` can be `\includegraphics`, TikZ pictures, PSTricks pictures, etc.


LaTeX compatibility
-------------------

Almost everything listed above is compatible to LaTeX, except:
* The `\begin{blockquote} ... \end{blockquote}` environment.
* The formula list environment `\begin{formulalist} \formula{...} ... \end{formulalist}`.
* The picture group environment `\begin{picturegroup} \picture{title}{commands} ... \end{picturegroup}`.
* The code command `\code` and environment `\begin{codelisting} ... \end{codelisting}`.
* The pixel width/height and alternative text of `\includegraphics[...]{...}`.

See below how for definitions in LaTeX which will allow to use almost all of these constructs in LaTeX documents.


Block quotes
------------

The block quote environment `blockquote` can be defined in LaTeX as follows:

``` .tex
\newenvironment{blockquote}%
  {\begin{quote}}%
  {\end{quote}}
```


Formula list
------------

The formula list environment `formulalist` can be defined in LaTeX as follows:

``` .tex
\usepackage{ifthen}
\newenvironment{formulalist}[1][1]
  {%
    \def\formulalistcols{#1}%
    \begin{list}{}{\rightmargin-0.5cm\leftmargin+0.5cm}\item[]%
    \ifnumequal{\formulalistcols}{1}{\begin{flushleft}}{\begin{multicols}{#1}}%
    \long\def\formula##1{\par\noindent##1}%
  }%
  {%
    \ifnumequal{\formulalistcols}{1}{\end{flushleft}}{\end{multicols}}%
    \end{list}%
  }
```


Picture group
-------------

The picture group environment `picturegroup` can be defined in LaTeX as follows:

``` .tex
\newenvironment{picturegroup}
  {%
    \begin{center}%
    \renewcommand{\arraystretch}{0.2}%
    \lineskip=10pt\baselineskip=0pt%
    \long\def\picture##1##2{\begin{tabular}[b]{c}\mbox{##2}\\\mbox{##1}\end{tabular}}%
  }%
  {%
    \end{center}%
  }
```


Code listings
-------------

The `\code` command and the `codelisting` environment can be defined in LaTeX as follows using the [`listings` package](https://www.ctan.org/pkg/listings):

``` .tex
\usepackage{listings}
\newcommand{\code}[1]{\lstset{language=#1}\lstinline}
\lstnewenvironment{codelisting}[1]{\lstset{language=#1}}{}
```

Note that `listings` is known to have problems with Unicode. Alternatively, you might be able to use the [`minted` package](https://www.ctan.org/pkg/minted).


Formulae backend
================

There are two available formulae backends:

 * one based on the [`latex_formula_renderer` plugin](https://plugins.getnikola.com/v7/latex_formula_renderer/);
 * one based on [MathJax](https://www.mathjax.org/).

You can choose which one by setting the `LATEX_FORMULA_RENDERER` configuration variable; default is `latex_formula_image_renderer`, which is based on the `latex_formula_renderer` plugin. See `conf.py.sample` for more information.

The first plugin allows special features the second doesn't:

 * `align` environments (see the [AMSMath documentation](ftp://ftp.ams.org/ams/doc/amsmath/amsldoc.pdf));
 * XY-pic diagrams (see the [XY-Pic user guide](http://texdoc.net/texmf-dist/doc/generic/xypic/xyguide.pdf));
 * PSTricks graphics (see [here](https://en.wikipedia.org/wiki/PSTricks) for more information);
 * TikZ pictures (see [here](https://en.wikibooks.org/wiki/LaTeX/PGF/TikZ) for more information).

You need an installed LaTeX distribution for this to work, with some extra tools. See the `latex_formula_renderer` plugin for details.


Required Translations
=====================

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
