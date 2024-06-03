from PySide6.QtWidgets import QGraphicsView,QGraphicsRectItem
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QPen, QPainter

from ObjectExplorer.AssetBase import AssetBase

class ModelView(QGraphicsView):
    def __init__(self, scene):
        super().__init__(scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setMouseTracking(True)
        self.setAcceptDrops(True)
        self.selection_rect = None
        self.origin = QPointF()
        self.is_dragging_item = False

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.origin = self.mapToScene(event.position().toPoint())
            item = self.itemAt(event.position().toPoint())
            if item:
                self.is_dragging_item = True
            else:
                self.selection_rect = QGraphicsRectItem(QRectF(self.origin, self.origin))
                self.selection_rect.setPen(QPen(Qt.blue, 2, Qt.DashLine))
                self.scene().addItem(self.selection_rect)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.selection_rect:
            rect = QRectF(self.origin, self.mapToScene(event.position().toPoint())).normalized()
            self.selection_rect.setRect(rect)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.selection_rect:
                items = self.scene().items(self.selection_rect.rect(), Qt.IntersectsItemShape)
                for item in items:
                    if isinstance(item, AssetBase):
                        item.setSelected(True)
                self.scene().removeItem(self.selection_rect)
                self.selection_rect = None
            self.is_dragging_item = False
        super().mouseReleaseEvent(event)