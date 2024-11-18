from PySide6.QtWidgets import QGraphicsView
from PySide6.QtCore import Signal
from PySide6.QtGui import QPainter


class ModelView(QGraphicsView):
    zoomChanged = Signal(float)

    def __init__(self, scene, mainWindow):
        super().__init__(scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setMouseTracking(True)

        self.zoomFactor = 1.0
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)

    def zoomIn(self):
        self.zoom(1.5) # Akash: This value need to discuss with Andrei

    def zoomOut(self):
        self.zoom(1 / 1.5) # Akash: This value need to discuss with Andrei

    def zoom(self, factor):
        self.zoomFactor *= factor
        self.scale(factor, factor)
        self.zoomChanged.emit(self.zoomFactor)

    def setZoom(self, zoomPercentage):
        factor = zoomPercentage / 100.0
        self.scale(factor / self.zoomFactor, factor / self.zoomFactor)
        self.zoomFactor = factor
        self.zoomChanged.emit(self.zoomFactor)

    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            self.zoomIn()
        else:
            self.zoomOut()

    # Handling all the mouse press/move/release event to QGraphicsScene ( ModelScene) derived class to avoid
    # collision of functionality in 2 different places( ModelView vs ModelScene).
