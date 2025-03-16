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

;; Use pygments highlighting for code
(defun pygmentize (lang code)
  "Use Pygments to highlight the given code and return the output"
  (with-temp-buffer
    (insert code)
    (let ((lang (get-pygments-language lang)))
      (shell-command-on-region (point-min) (point-max)
                               (if lang
                                   (format "pygmentize -f html -l %s" lang)
                                 "pygmentize -f html -g")
                               (buffer-name) t))
    (buffer-string)))

(defconst org-pygments-language-alist
  '(("asymptote" . "asymptote")
    ("awk" . "awk")
    ("c" . "c")
    ("console" . "console")
    ("c++" . "cpp")
    ("cpp" . "cpp")
    ("clojure" . "clojure")
    ("css" . "css")
    ("d" . "d")
    ("emacs-lisp" . "emacs-lisp")
    ("elisp" . "elisp")
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
    ("shell-session" . "shell-session")
    ("sql" . "sql")
    ("sqlite" . "sqlite3")
    ("tcl" . "tcl")
    ("text" . "text"))
  "Alist between org-babel languages and Pygments lexers.
lang is downcased before assoc, so use lowercase to describe language available.
See: http://orgmode.org/worg/org-contrib/babel/languages.html and
http://pygments.org/docs/lexers/ for adding new languages to the mapping.")

(defvar org-pygments-detected-languages nil
  "List of languages supported by Pygments, detected at runtime.")

(defun get-pygments-language (lang)
  "Try to find a Pygments lexer that matches the provided language."
  (let ((pygmentize-lang (cdr (assoc lang org-pygments-language-alist))))
    (if pygmentize-lang
        pygmentize-lang
      (when (null org-pygments-detected-languages)
        (with-temp-buffer
          ;; Extracts supported languages from "pygmentize -L lexers --json"
          (setq org-pygments-detected-languages
                (if (= 0 (call-process "pygmentize" nil (current-buffer) nil
                                       "-L" "lexers" "--json"))
                    (progn
                      (goto-char (point-min))
                      (if (featurep 'json)
                          ;; Use json to parse supported languages
                          (let ((lexers (alist-get 'lexers
                                                   (json-parse-buffer
                                                    :object-type 'alist
                                                    :array-type 'list))))
                            (mapcan (lambda (lexer)
                                      (alist-get 'aliases (cdr lexer)))
                                    lexers))
                        ;; Use regexp on a best effort basis
                        (let ((case-fold-search nil) langs)
                          (while (re-search-forward "\"\\([a-z+#/-]+\\)\""
                                                    nil t)
                            (let ((s (match-string 1)))
                              (unless (member s '("lexers" "aliases"
                                                  "filenames" "mimetypes"))
                                (push s langs))))
                          langs)))
                  ;; Fallback
                  '("text")))))
      (if (member lang org-pygments-detected-languages) lang))))

;; Override the html export function to use pygments
(define-advice org-html-src-block (:around (old-src-block src-block contents info))
  "Transcode a SRC-BLOCK element from Org to HTML.
CONTENTS holds the contents of the item.  INFO is a plist holding
contextual information."
  (if (or (not nikola-use-pygments)
          (org-export-read-attribute :attr_html src-block :textarea))
      (funcall old-src-block src-block contents info)
    (let ((lang (or (org-element-property :language src-block) ""))
          (code (car (org-export-unravel-code src-block))))
      (pygmentize (downcase lang) code))))

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

;; Support for magic links (link:// scheme)
(org-link-set-parameters
 "link"
 :export (lambda (path desc backend)
           (cond
            ((eq 'html backend)
             (format "<a href=\"link:%s\">%s</a>"
                     path (or desc path))))))

;; Export function used by Nikola.
(defun nikola-html-export (infile outfile)
  "Export the body only of the input file and write it to
specified location."
  (with-current-buffer (find-file infile)
    (org-macro-replace-all nikola-macro-templates)
    (org-html-export-as-html nil nil t t)
    (write-file outfile nil)))
