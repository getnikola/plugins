;; Init file to use with the orgmode plugin.

;; Load org-mode
;; Requires org-mode v8.x

;; Uncomment these lines and change the path to your org source to
;; add use it.
;; (let* ((org-lisp-dir "~/.emacs.d/src/org/lisp"))
;;   (when (file-directory-p org-lisp-dir)
;;       (add-to-list 'load-path org-lisp-dir)
;;       (require 'org)))

(require 'ox-html)

;; Custom configuration for the export.
;;; Add any custom configuration that you would like.
(setq
 org-export-with-toc nil
 org-export-with-section-numbers nil
 org-startup-folded 'showeverything)

;; Load additional configuration from conf.el
(let ((conf (expand-file-name "conf.el" (file-name-directory load-file-name))))
  (if (file-exists-p conf)
      (load-file conf)))

;; Export function used by Nikola.
(defun nikola-html-export (infile outfile)
  "Export the body only of the input file and write it to
specified location."

  (with-current-buffer (find-file infile)
    (org-html-export-as-html nil nil t t)
    (write-file outfile nil)))
