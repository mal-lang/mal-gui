from PySide6.QtCore import QRectF, Qt,QPointF
from PySide6.QtGui import QPixmap, QFont, QColor,QBrush,QPen
from PySide6.QtWidgets import  QGraphicsItem

from .EditableTextItem import EditableTextItem

class AssetBase(QGraphicsItem):
    
    assetSequenceId = 100 #Starting Sequence Id with normal start at 100(randomly taken)
    
    def __init__(self, assetType, assetName, imagePath, parent=None):
        super().__init__(parent)
        self.setZValue(1)  # rect items are on top
        self.assetType = assetType
        self.assetName = assetName
        self.assetSequenceId = AssetBase.generateNextSequenceId() #For Test only this field was added. Need to rethink design with respect to mal toolbox
        self.imagePath = imagePath
        self.image = QPixmap(self.imagePath).scaled(35, 35, Qt.KeepAspectRatio)  # Scale the image here

        self.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemSendsGeometryChanges)

        # Create the editable text item for block type
        self.typeTextItem = EditableTextItem(self.assetName, self)
        self.typeTextItem.lostFocus.connect(self.updateAssetName)

        self.connections = []
        self.initial_position = QPointF()
        
    @classmethod
    def generateNextSequenceId(cls):
        print("generateNextSequenceId is called")
        cls.assetSequenceId += 1
        return cls.assetSequenceId

    def boundingRect(self):
        # Define the bounding rectangle dimensions
        rectWidth = 300  # Adjust width as necessary
        rectHeight = 60
        return QRectF(0, 0, rectWidth, rectHeight)

    def paint(self, painter, option, widget):
        rect = self.boundingRect()
        
        # Draw the rectangle
        painter.setBrush(Qt.white)
        painter.setPen(Qt.black)
        
        # if self.isSelected():
        #     painter.setBrush(QBrush(QColor(0, 255, 0, 100)))  # Highlight color with transparency
        # else:
        #     painter.setBrush(Qt.white)  # Normal color

        if self.isSelected():
            pen = QPen(QColor(0, 0, 255), 4)  # Blue border with a thickness of 4(TBD)
            painter.setPen(pen)
            painter.drawRect(rect)

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
        painter.drawText(nameRect, Qt.AlignLeft | Qt.AlignVCenter, self.assetType)

        # Set position for the type text item (bottom half of rectangle)
        self.typeTextItem.setPos(75, rect.height() / 2 )  # Adjusted position

    def addConnection(self, connection):
        self.connections.append(connection)
        
    def removeConnection(self, connection):
        if connection in self.connections:
            self.connections.remove(connection)

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

    def updateAssetName(self):
        self.assetName = self.typeTextItem.toPlainText()
        self.typeTextItem.setTextInteractionFlags(Qt.NoTextInteraction)
        self.typeTextItem.deselectText()
        if self.assetType == "Attacker":
            self.attackerAttachment.name = self.assetName
        else:
            self.asset.name = self.assetName
        
        associatedScene = self.typeTextItem.scene()
        if associatedScene:
            print("Asset Name Changed by user")
            #Update the Object Explorer when number of items change
            associatedScene.mainWindow.updateChildsInObjectExplorerSignal.emit()


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
            
    def getItemAttributeValues(self):
        return {
            "Asset Sequence ID" : self.assetSequenceId,
            "Asset Name" : self.assetName,
            "Asset Type" : self.assetType
        }
