from PySide6.QtCore import QRectF, Qt, QPointF, QSize, QSizeF, QTimer
from PySide6.QtGui import (
    QPixmap,
    QFont,
    QColor,
    QBrush,
    QPen,
    QPainterPath,
    QFontMetrics,
    QLinearGradient,
    QImage
)
from PySide6.QtWidgets import  QGraphicsItem

from .EditableTextItem import EditableTextItem

class AssetBase(QGraphicsItem):
    assetSequenceId = 100  # Starting Sequence Id with normal start at 100(randomly taken) 

    def __init__(self, assetType, assetName, imagePath, parent=None):
        super().__init__(parent)
        self.setZValue(1)  # rect items are on top
        self.assetType = assetType
        self.assetName = assetName
        self.assetSequenceId = AssetBase.generateNextSequenceId()
        self.imagePath = imagePath
        print("image path = ", self.imagePath)

        # self.image = QPixmap(self.imagePath).scaled(30, 30, Qt.KeepAspectRatio)  # Scale the image here
        # self.image = QPixmap(self.imagePath)
        self.image = self.loadImageWithQuality(self.imagePath, QSize(512, 512))

        self.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemSendsGeometryChanges)

        # Create the editable text item for block type
        self.typeTextItem = EditableTextItem(self.assetName, self)
        self.typeTextItem.lostFocus.connect(self.updateAssetName)

        self.connections = []
        self.initial_position = QPointF()

        # Visual Styling
        self.width = 240
        self.height = 70
        self.size = QRectF(-self.width / 2, -self.height / 2, self.width, self.height)

        self.assetTypeBackgroundColor = QColor(0, 200, 0) #Green
        self.assetNameBackgroundColor = QColor(20, 20, 20, 200) # Gray

        self.iconPath = None
        self.iconVisible = True
        self.iconPixmap = QPixmap()

        self.titlePath = QPainterPath()  # The path for the title
        self.typePath = QPainterPath()  # The path for the type
        self.statusPath = QPainterPath()  # A path showing the status of the node

        self.horizontalMargin = 15  # Horizontal margin
        self.verticalMargin = 15  # Vertical margin
        
        self.timer = QTimer()
        self.statusColor =  QColor(0, 255, 0)
        self.attackerToggleState = False
        self.timer.timeout.connect(self.updateStatusColor)
        #timer to trigger every 500ms (0.5 seconds)
        self.timer.start(500)

        self.build()

    @classmethod
    def generateNextSequenceId(cls):
        cls.assetSequenceId += 1
        return cls.assetSequenceId

    def boundingRect(self):
        return self.size

    def paint(self, painter, option, widget=None):
        painter.setPen(self.assetNameBackgroundColor.lighter())
        painter.setBrush(self.assetNameBackgroundColor)
        painter.drawPath(self.path)

        gradient = QLinearGradient()
        gradient.setStart(0, -90)
        gradient.setFinalStop(0, 0)
        gradient.setColorAt(0, self.assetTypeBackgroundColor)  # Start color
        gradient.setColorAt(1, self.assetTypeBackgroundColor.darker())  # End color

        painter.setBrush(QBrush(gradient))
        painter.setPen(self.assetTypeBackgroundColor)
        painter.drawPath(self.titleBgPath.simplified())

        painter.setPen(Qt.NoPen)
        painter.setBrush(Qt.white)
        painter.drawPath(self.titlePath)
        painter.drawPath(self.typePath)

        # Draw the status path
        painter.setBrush(self.statusColor)
        painter.setPen(self.statusColor.darker())
        painter.drawPath(self.statusPath.simplified())

        # Draw the icon if it's visible
        if self.iconVisible and not self.image.isNull():
            targetIconSize = QSize(24, 24)  # Desired size for the icon

            # Resize the icon using smooth transformation
            # resizedImageIcon = self.image.scaled(targetIconSize, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            resizedImageIcon = self.image


            # Calculate the position and size for the icon background
            iconRect = QRectF(-self.width / 2 + 10, -self.height / 2 + 10, targetIconSize.width(), targetIconSize.height())
            margin = 5  # Margin around the icon

            # Draw the background for the icon with additional margin
            backgroundRect = QRectF(
                iconRect.topLeft() - QPointF(margin, margin),
                QSizeF(targetIconSize.width() + 2 * margin, targetIconSize.height() + 2 * margin)
            )
            painter.setBrush(Qt.white)  # Set the brush color to white
            painter.drawRect(backgroundRect.toRect())  # Convert QRectF to QRect and draw the white background rectangle

            # Draw the resized icon on top of the white background
            painter.drawPixmap(iconRect.toRect(), resizedImageIcon)  # Convert QRectF to QRect and draw the resized icon

        # Draw the highlight if selected
        if self.isSelected():
            painter.setPen(QPen(self.assetTypeBackgroundColor.lighter(), 2))
            painter.setBrush(Qt.NoBrush)
            painter.drawPath(self.path)


    def build(self):
        self.titleText = self.assetType
        self.titlePath = QPainterPath()
        self.typePath = QPainterPath()
        self.statusPath = QPainterPath()

        # Set the font for title and category
        titleFont = QFont("Arial", pointSize=12)
        typeFont = QFont("Arial", pointSize=12)

        # Use fixed width and height
        fixedWidth = self.width
        fixedHeight = self.height

        # Draw the background of the node
        self.path = QPainterPath()
        self.path.addRoundedRect(-fixedWidth / 2, -fixedHeight / 2, fixedWidth, fixedHeight, 6, 6)

        self.titleBgPath = QPainterPath()
        self.titleBgPath.addRoundedRect(-fixedWidth / 2, -fixedHeight / 2, fixedWidth, titleFont.pointSize() + 2 * self.verticalMargin, 6, 6)

        # Draw status path
        self.statusPath.setFillRule(Qt.WindingFill)
        self.statusPath.addRoundedRect(fixedWidth / 2 - 12, -fixedHeight / 2 + 2, 10, 10, 2, 2)

        # Center title in the upper half
        titleFontMetrics = QFontMetrics(titleFont)
        self.titlePath.addText(
            -titleFontMetrics.horizontalAdvance(self.titleText) / 2,  # Center horizontally
            -fixedHeight / 2 + self.verticalMargin + titleFontMetrics.ascent(),  # Center vertically within its section
            titleFont,
            self.titleText
        )

        # Set the font and default color for typeTextItem
        self.typeTextItem.setFont(typeFont)
        self.typeTextItem.setDefaultTextColor(Qt.white)  # Set text color to white

        # Initial position of typeTextItem
        self.updateTypeTextItemPosition()

        # Connect the lostFocus signal to update the position when the text loses focus
        self.typeTextItem.lostFocus.connect(self.updateTypeTextItemPosition)

        # self.widget.move(-self.widget.size().width() / 2, fixedHeight / 2 - self.widget.size().height() + 5)

    def updateTypeTextItemPosition(self):
        #to update the position of the typeTextItem so that it remains centered within the lower half of the node whenever the text changes.

        typeFontMetrics = QFontMetrics(self.typeTextItem.font())
        fixedHeight = self.height
        titleFontMetrics = QFontMetrics(QFont("Arial", pointSize=12))

        # Calculate the new position for typeTextItem
        typeTextItemPosX = -typeFontMetrics.horizontalAdvance(self.typeTextItem.toPlainText()) / 2
        typeTextItemPosY = -fixedHeight / 2 + titleFontMetrics.height() + 2 * self.verticalMargin

        # Update position
        self.typeTextItem.setPos(typeTextItemPosX, typeTextItemPosY)
        
        #For Attacker make the background of type As Red - Change Request from Professor Mathias
        if self.assetType == 'Attacker':
            self.assetTypeBackgroundColor = QColor(255, 0, 0) #Red

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
            if self.scene():
                self.scene().update()  # Ensure the scene is updated - this fixed trailing borders issue
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
        
        self.updateTypeTextItemPosition()
        
        if self.assetType == "Attacker":
            self.attackerAttachment.name = self.assetName
        else:
            self.asset.name = self.assetName
        associatedScene = self.typeTextItem.scene()
        if associatedScene:
            print("Asset Name Changed by user")
            associatedScene.mainWindow.updateChildsInObjectExplorerSignal.emit()

    def focusOutEvent(self, event):
        self.typeTextItem.clearFocus()
        super().focusOutEvent(event)

    def mousePressEvent(self, event):
        self.initial_position = self.pos()

        if self.typeTextItem.hasFocus() and not self.typeTextItem.contains(event.pos()):
            self.typeTextItem.clearFocus()
        elif not self.typeTextItem.contains(event.pos()):
            self.typeTextItem.deselectText()
        else:
            super().mousePressEvent(event)

    def getItemAttributeValues(self):
        return {
            "Asset Sequence ID": self.assetSequenceId,
            "Asset Name": self.assetName,
            "Asset Type": self.assetType
        }

    def setIcon(self, iconPath=None):
        self.iconPath = iconPath
        if self.image:
            self.iconPixmap = QPixmap(iconPath)
        else:
            self.iconPixmap = QPixmap()

    def toggleIconVisibility(self):
        self.iconVisible = not self.iconVisible
        self.update()

    def updateStatusColor(self):
        if self.assetType =='Attacker':
            self.attackerToggleState = not self.attackerToggleState
            if self.attackerToggleState:
                self.statusColor =  QColor(0, 255, 0) #Green
            else: 
                self.statusColor =  QColor(255, 0, 0) #Red
        
        #Otherwise return Green for all assets
        else:
            self.statusColor =  QColor(0, 255, 0)
        
        self.update()
    
    def loadImageWithQuality(self, path, size):
        image = QImage(path)
        if not image.isNull():
            return QPixmap.fromImage(image.scaled(size, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        return QPixmap()
        
