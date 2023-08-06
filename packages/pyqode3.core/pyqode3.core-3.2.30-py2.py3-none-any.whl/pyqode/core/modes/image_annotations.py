# -*- coding: utf-8 -*-
"""
This module contains the image annotations mode. This mode allows annotations
to be sent to the backend, and adds annotations as user data to text blocks.
The annotations are shown in the ImageAnnotationsPanel.
"""
from pyqode.qt import QtGui, QtCore
from pyqode.core.modes import CheckerMode
from pyqode.core.backend.workers import (
    image_annotations,
    set_image_annotations
)

TOOLTIP = '<img style="background-color:white;" src="{}" />'


class ImageAnnotationsMode(CheckerMode):
    
    annotation_clicked = QtCore.Signal(object, object)
    
    def __init__(self, annotations={}):
        CheckerMode.__init__(self, image_annotations, underline=False)
    
    def set_annotations(self, annotations):
        self.editor.backend.send_request(set_image_annotations, annotations)
        self.request_analysis()

    def message_icon(self, msg):
        return QtGui.QIcon(msg.path)
        
    def message_tooltip(self, msg):
        return TOOLTIP.format(msg.path)

    def show_on_panel(self, panel):
        return panel.__class__.__name__ == 'ImageAnnotationsPanel'

    def message_clicked(self, msg, event):
        self.annotation_clicked.emit(msg, event)
