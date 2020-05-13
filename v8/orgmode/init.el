;; Init file to use with the orgmode plugin.

;; Load org-mode
;; Requires org-mode v8.x

(require 'package)
(setq package-load-list '((htmlize t)))
(package-initialize)

(require 'org)
(require 'ox-html)

;;; Custom configuration for the export.

;;; Add any custom configuration that you would like to 'conf.el'.
(setq nikola-use-pygments t
      org-export-with-toc nil
      org-export-with-section-numbers nil
      org-startup-folded 'showeverything)

;; Load additional configuration from conf.el
(let ((conf (expand-file-name "conf.el" (file-name-directory load-file-name))))
  (if (file-exists-p conf)
      (load-file conf)))

;;; Macros

;; Load Nikola macros
(setq nikola-macro-templates
      (with-current-buffer
          (find-file
           (expand-file-name "macros.org" (file-name-directory load-file-name)))
        (org-macro--collect-macros)))

;;; Code highlighting
(defun org-html-decode-plain-text (text)
  "Convert HTML character to plain TEXT. i.e. do the inversion of
     `org-html-encode-plain-text`. Possible conversions are set in
     `org-html-protect-char-alist'."
  (mapc
   (lambda (pair)
     (setq text (replace-regexp-in-string (cdr pair) (car pair) text t t)))
   (reverse org-html-protect-char-alist))
  text)

;; Use pygments highlighting for code
(defun pygmentize (lang code)
  "Use Pygments to highlight the given code and return the output"
  (with-temp-buffer
    (insert code)
    (let ((lang (or (cdr (assoc lang org-pygments-language-alist)) "text")))
      (shell-command-on-region (point-min) (point-max)
                               (format "pygmentize -f html -l %s" lang)
                               (buffer-name) t))
    (buffer-string)))

(defconst org-pygments-language-alist
  '(("asymptote" . "asymptote")
    ("awk" . "awk")
    ("c" . "c")
    ("c++" . "cpp")
    ("cpp" . "cpp")
    ("clojure" . "clojure")
    ("css" . "css")
    ("d" . "d")
    ("emacs-lisp" . "scheme")
    ("F90" . "fortran")
    ("gnuplot" . "gnuplot")
    ("groovy" . "groovy")
    ("haskell" . "haskell")
    ("java" . "java")
    ("js" . "js")
    ("julia" . "julia")
    ("latex" . "latex")
    ("lisp" . "lisp")
    ("makefile" . "makefile")
    ("matlab" . "matlab")
    ("mscgen" . "mscgen")
    ("ocaml" . "ocaml")
    ("octave" . "octave")
    ("perl" . "perl")
    ("picolisp" . "scheme")
    ("python" . "python")
    ("r" . "r")
    ("ruby" . "ruby")
    ("sass" . "sass")
    ("scala" . "scala")
    ("scheme" . "scheme")
    ("sh" . "sh")
    ("sql" . "sql")
    ("sqlite" . "sqlite3")
    ("tcl" . "tcl"))
  "Alist between org-babel languages and Pygments lexers.
lang is downcased before assoc, so use lowercase to describe language available.
See: http://orgmode.org/worg/org-contrib/babel/languages.html and
http://pygments.org/docs/lexers/ for adding new languages to the mapping.")

;; Override the html export function to use pygments
(defun org-html-src-block (src-block contents info)
  "Transcode a SRC-BLOCK element from Org to HTML.
CONTENTS holds the contents of the item.  INFO is a plist holding
contextual information."
  (if (org-export-read-attribute :attr_html src-block :textarea)
      (org-html--textarea-block src-block)
    (let ((lang (org-element-property :language src-block))
          (code (org-element-property :value src-block))
          (code-html (org-html-format-code src-block info)))
      (if nikola-use-pygments
          (progn
            (unless lang (setq lang ""))
            (pygmentize (downcase lang) (org-html-decode-plain-text code)))
        code-html))))

;; Export images with custom link type
(defun org-custom-link-img-url-export (path desc format)
  (cond
   ((eq format 'html)
    (format "<img src=\"%s\" alt=\"%s\"/>" path desc))))
(org-add-link-type "img-url" nil 'org-custom-link-img-url-export)

;; Export images with built-in file scheme
(defun org-file-link-img-url-export (path desc format)
  (cond
   ((eq format 'html)
    (format "<img src=\"/%s\" alt=\"%s\"/>" path desc))))
(org-add-link-type "file" nil 'org-file-link-img-url-export)

;; Export function used by Nikola.
(defun nikola-html-export (infile outfile)
  "Export the body only of the input file and write it to
specified location."
  (with-current-buffer (find-file infile)
    (org-macro-replace-all nikola-macro-templates)
    (org-html-export-as-html nil nil t t)
    (write-file outfile nil)))
