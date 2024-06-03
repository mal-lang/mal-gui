from PySide6.QtCore import QRectF, Qt,QPointF
from PySide6.QtGui import QPixmap, QFont, QColor,QBrush
from PySide6.QtWidgets import  QGraphicsItem

from .EditableTextItem import EditableTextItem

class AssetBase(QGraphicsItem):
    def __init__(self, assetNameUpper, assetNameLower, imagePath, parent=None):
        super().__init__(parent)
        self.setZValue(1)  # rect items are on top
        self.assetNameUpper = assetNameUpper
        self.assetNameLower = assetNameLower
        self.imagePath = imagePath
        self.image = QPixmap(self.imagePath).scaled(35, 35, Qt.KeepAspectRatio)  # Scale the image here

        self.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemSendsGeometryChanges)

        # Create the editable text item for block type
        self.typeTextItem = EditableTextItem(self.assetNameLower, self)
        self.typeTextItem.lostFocus.connect(self.updateassetNameLower)

        self.connections = []
        self.initial_position = QPointF()

    def boundingRect(self):
        # Define the bounding rectangle dimensions
        rectWidth = 300  # Adjust width as necessary
        rectHeight = 60
        return QRectF(0, 0, rectWidth, rectHeight)

    def paint(self, painter, option, widget):
        rect = self.boundingRect()
        
        # Draw the rectangle
        painter.setBrush(Qt.white)
        
        # if self.isSelected():
        #     painter.setBrush(QBrush(QColor(0, 255, 0, 100)))  # Highlight color with transparency
        # else:
        #     painter.setBrush(Qt.white)  # Normal color

        painter.setPen(Qt.black)
        painter.drawRect(rect)

        # Draw the image
        imageRect = QRectF(10, (rect.height() - 40) / 2, 40, 40)  # Center the image vertically
        painter.drawPixmap(imageRect.toRect(), self.image)

        # Set font size, increased by 10%
        fontSize = 12 * 1.2

        # Set font for block name (light font)
        lightFont = QFont("Arial", fontSize, QFont.Light)
        painter.setFont(lightFont)

        # Draw block name (upper half of rectangle)
        nameRect = QRectF(80, 5, rect.width() - 90, rect.height() / 2 - 10)
        painter.setPen(QColor(100, 100, 100))
        painter.drawText(nameRect, Qt.AlignLeft | Qt.AlignVCenter, self.assetNameUpper)

        # Set position for the type text item (bottom half of rectangle)
        self.typeTextItem.setPos(75, rect.height() / 2 )  # Adjusted position

    def addConnection(self, connection):
        self.connections.append(connection)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            if self.pos() != self.initial_position:
                for connection in self.connections:
                    connection.updatePath()
                self.initial_position = self.pos()
        return super().itemChange(change, value)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.typeTextItem.setTextInteractionFlags(Qt.TextEditorInteraction)
            self.typeTextItem.setFocus()
            self.typeTextItem.selectAllText()  # Select all text when activated
            event.accept()
        else:
            event.ignore()

    def updateassetNameLower(self):
        self.assetNameLower = self.typeTextItem.toPlainText()
        self.typeTextItem.setTextInteractionFlags(Qt.NoTextInteraction)
        self.typeTextItem.deselectText()

    def focusOutEvent(self, event):
        # Clear focus from typeTextItem when focus is lost
        self.typeTextItem.clearFocus()
        super().focusOutEvent(event)

    def mousePressEvent(self, event):
        # Store the initial position when the item is clicked
        self.initial_position = self.pos()
        
        if self.typeTextItem.hasFocus() and not self.typeTextItem.contains(event.pos()):
            self.typeTextItem.clearFocus()
        elif not self.typeTextItem.contains(event.pos()):
            self.typeTextItem.deselectText()
        else:
            super().mousePressEvent(event)