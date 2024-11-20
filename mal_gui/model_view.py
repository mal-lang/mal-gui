from PySide6.QtWidgets import QGraphicsView
from PySide6.QtCore import Signal
from PySide6.QtGui import QPainter


class ModelView(QGraphicsView):
    zoom_changed = Signal(float)

    def __init__(self, scene, main_window):
        super().__init__(scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setMouseTracking(True)

        self.zoom_factor = 1.0
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)

    def zoomIn(self):
        """Overrides base"""
        self.zoom(1.5) # Akash: This value need to discuss with Andrei

    def zoomOut(self):
        """Overrides base"""
        self.zoom(1 / 1.5) # Akash: This value need to discuss with Andrei

    def wheelEvent(self, event):
        """Overrides base"""
        if event.angleDelta().y() > 0:
            self.zoomIn()
        else:
            self.zoomOut()

    def zoom(self, factor):
        """Zoom one step with given factor"""
        self.zoom_factor *= factor
        self.scale(factor, factor)
        self.zoom_changed.emit(self.zoom_factor)

    def set_zoom(self, zoom_percentage):
        """Set zoom to certain value"""
        factor = zoom_percentage / 100.0
        self.scale(factor / self.zoom_factor, factor / self.zoom_factor)
        self.zoom_factor = factor
        self.zoom_changed.emit(self.zoom_factor)

    # Handling all the mouse press/move/release event to QGraphicsScene ( ModelScene) derived class to avoid
    # collision of functionality in 2 different places( ModelView vs ModelScene).
