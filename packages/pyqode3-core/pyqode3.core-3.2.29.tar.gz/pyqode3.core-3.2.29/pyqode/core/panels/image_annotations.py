# -*- coding: utf-8 -*-
"""
This module contains the image annotations panel, which shows the image
annotations in the marging of the editor. The annotations are managed by the
ImageAnnotationsMode.
"""

from pyqode.core.panels import CheckerPanel
from pyqode.qt import QtCore


class ImageAnnotationsPanel(CheckerPanel):
    
    _adjust_vertical_offset = False
    
    def __init__(self):
        self._shown_size_hint = QtCore.QSize(256, 256)
        self._hidden_size_hint = QtCore.QSize(1, 1)
        self._size_hint = self._hidden_size_hint
        CheckerPanel.__init__(self)
    
    def sizeHint(self):
        return self._size_hint
    
    def _icon_size(self):
        return self.sizeHint()
    
    def _multiple_markers_icon(self):
        return
    
    def _vertical_offset(self):
        return 0

    def _message_count(self, n):
        # When there are annotations, the size hint of the panel is changed so
        # that it becomes visible. Otherwise, the size hint is reduced to 1 so
        # that it's practically invisible but still functional.
        new_hint = self._shown_size_hint if n else self._hidden_size_hint
        if new_hint == self._size_hint:
            return
        self._size_hint = new_hint
        self.editor.panels.refresh()
