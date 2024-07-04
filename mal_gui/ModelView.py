from PySide6.QtWidgets import QGraphicsView,QGraphicsRectItem
from PySide6.QtCore import Qt, QRectF, QPointF, Signal
from PySide6.QtGui import QPen, QPainter

from ObjectExplorer.AssetBase import AssetBase

class ModelView(QGraphicsView):
    zoomChanged = Signal(float)

    def __init__(self, scene, mainWindow):
        super().__init__(scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setMouseTracking(True)
        self.setAcceptDrops(True)
        self.selectionRect = None
        self.origin = QPointF()
        self.isDraggingItem = False
        self.mainWindow = mainWindow

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

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.origin = self.mapToScene(event.position().toPoint())
            item = self.itemAt(event.position().toPoint())
            if item:
                self.isDraggingItem = True
            else:
                self.selectionRect = QGraphicsRectItem(QRectF(self.origin, self.origin))
                self.selectionRect.setPen(QPen(Qt.blue, 2, Qt.DashLine))
                self.scene().addItem(self.selectionRect)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.selectionRect:
            rect = QRectF(self.origin, self.mapToScene(event.position().toPoint())).normalized()
            self.selectionRect.setRect(rect)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.selectionRect:
                items = self.scene().items(self.selectionRect.rect(), Qt.IntersectsItemShape)
                selected_assets = []
                for item in items:
                    if isinstance(item, AssetBase):
                        item.setSelected(True)
                        if item.assetType != "Attacker":
                            selected_assets.append(item.asset)
                if len(selected_assets) == 1:
                    asset = selected_assets[0]
                    self.mainWindow.updatePropertiesWindow(asset)
                self.scene().removeItem(self.selectionRect)
                self.selectionRect = None
            self.isDraggingItem = False
        super().mouseReleaseEvent(event)
