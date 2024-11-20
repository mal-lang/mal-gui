from PySide6.QtWidgets import QGraphicsRectItem
from PySide6.QtGui import QBrush, QColor, QPen

class AssetsContainerRectangleBox(QGraphicsRectItem):
    def __init__(self, rect, parent=None):
        super().__init__(rect, parent)

        self.setBrush(QBrush(QColor(0, 0, 255, 50))) #Blue
        self.setPen(QPen(QColor(0, 0, 255, 50))) #Blue
