;; Topographica mode for Emacs
;; $Id$

(define-derived-mode Topographica-mode
  python-mode "Topographica"
  "Major mode for editing Topographica scripts.

At present, inherits directly from Python mode, but customizations are
likely in the future.

\\{Topographica-mode-map}
")

(add-to-auto-mode-alist ".ty$"  'Topographica-mode)

