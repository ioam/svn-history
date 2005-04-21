;; Topographica mode for Emacs
;; $Id$

;;; To use this mode, add the following lines to your .emacs file:
;;;
;;; (add-to-list 'load-path "$TOPO/etc/")
;;; (autoload 'Topographica-mode "topographica.elc" "Topographica mode" t)
;;; (add-to-auto-mode-alist ".ty$"  'Topographica-mode)
;;;
;;; where $TOPO is the path to your topographica/ directory.

(define-derived-mode Topographica-mode
  python-mode "Topographica"
  "Major mode for editing Topographica scripts.

At present, inherits directly from Python mode, but customizations are
likely in the future.

\\{Topographica-mode-map}
")

(add-to-auto-mode-alist ".ty$"  'Topographica-mode)

