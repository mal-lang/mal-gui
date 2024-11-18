from PySide6.QtCore import QRectF, Qt,QPointF,QSize,QSizeF,QTimer
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

from ..ObjectExplorer.EditableTextItem import EditableTextItem
from .AssetsContainerRectangleBox import AssetsContainerRectangleBox

class AssetsContainer(QGraphicsItem):
    containerSequenceId = 100  # Starting Sequence Id with normal start at 100(randomly taken) 
    
    def __init__(self, containerType, containerName, imagePath,plusSymbolImagePath,minusSymbolImagePath, parent=None):
        super().__init__(parent)
        self.setZValue(1)  # rect items are on top
        self.containerType = containerType
        self.containerName = containerName
        self.containerSequenceId = AssetsContainer.generateNextSequenceId()
        self.imagePath = imagePath
        self.plusSymbolImagePath = plusSymbolImagePath
        self.minusSymbolImagePath = minusSymbolImagePath
        self.plusOrMinusSymbolImageRect = QRectF()
        self.isPlusSymbolVisible = True  # Track the current symbol state
        self.containerBox = None
        print("image path = "+ self.imagePath)

        self.image = self.loadImageWithQuality(self.imagePath, QSize(512, 512))
        self.plusSymbolImage = self.loadImageWithQuality(self.plusSymbolImagePath, QSize(512, 512))
        self.minusSymbolImage = self.loadImageWithQuality(self.minusSymbolImagePath, QSize(512, 512))

        self.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemSendsGeometryChanges)

        # Create the editable text item for block type
        self.typeTextItem = EditableTextItem(self.containerName, self)
        self.typeTextItem.lostFocus.connect(self.updateContainerName)

        self.containerizedAssetsList = []
        self.initialPosition = QPointF()

        # Visual Styling
        self.width = 240
        self.height = 70
        self.size = QRectF(-self.width / 2, -self.height / 2, self.width, self.height)

        self.containerTypeBackgroundColor = QColor(0, 200, 255) #Blue
        self.containerNameBackgroundColor = QColor(20, 20, 20, 200) # Gray

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
        cls.containerSequenceId += 1
        return cls.containerSequenceId

    def boundingRect(self):
        return self.size

    def paint(self, painter, option, widget=None):
        painter.setPen(self.containerNameBackgroundColor.lighter())
        painter.setBrush(self.containerNameBackgroundColor)
        painter.drawPath(self.path)

        gradient = QLinearGradient()
        gradient.setStart(0, -90)
        gradient.setFinalStop(0, 0)
        gradient.setColorAt(0, self.containerTypeBackgroundColor)  # Start color
        gradient.setColorAt(1, self.containerTypeBackgroundColor.darker())  # End color

        painter.setBrush(QBrush(gradient))
        painter.setPen(self.containerTypeBackgroundColor)
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

        # Determine which symbol to draw based on the current state
        currentSymbolImage = self.plusSymbolImage if self.isPlusSymbolVisible else self.minusSymbolImage
        if not currentSymbolImage.isNull():
            targetSymbolImageSize = QSize(12, 12)  # Desired size for the second icon

            # Get the bounding rect of the titleBgPath
            titleBgRect = self.titleBgPath.boundingRect()

            # Calculate the position for the symbol at the bottom-right corner of titleBgPath
            self.plusOrMinusSymbolImageRect = QRectF(
                titleBgRect.right() - targetSymbolImageSize.width() - 10,  # x position
                titleBgRect.bottom() - targetSymbolImageSize.height() - 5,  # y position
                targetSymbolImageSize.width(),
                targetSymbolImageSize.height()
            )
            
            painter.setBrush(Qt.white)
            painter.drawRect(self.plusOrMinusSymbolImageRect)
            
            resizedSymbolImage = currentSymbolImage.scaled(targetSymbolImageSize, Qt.KeepAspectRatio, Qt.SmoothTransformation)

            # Draw the plus or minus symbol with a white background
            painter.drawPixmap(self.plusOrMinusSymbolImageRect.toRect(), resizedSymbolImage)



        # Draw the highlight if selected
        if self.isSelected():
            painter.setPen(QPen(self.containerTypeBackgroundColor.lighter(), 2))
            painter.setBrush(Qt.NoBrush)
            painter.drawPath(self.path)


    def build(self):
        self.titleText = self.containerType
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


    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            if self.pos() != self.initialPosition:
                self.initialPosition = self.pos()
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

    def updateContainerName(self):
        self.containerName = self.typeTextItem.toPlainText()
        self.typeTextItem.setTextInteractionFlags(Qt.NoTextInteraction)
        self.typeTextItem.deselectText()
        
        self.updateTypeTextItemPosition()
        
        # self.container.name = self.containerName
        
        associatedScene = self.typeTextItem.scene()
        if associatedScene:
            print("Container Name Changed by user")

    def focusOutEvent(self, event):
        self.typeTextItem.clearFocus()
        super().focusOutEvent(event)

    def mousePressEvent(self, event):
        self.initialPosition = self.pos()

        if self.plusOrMinusSymbolImageRect.contains(event.pos()):
            print("Plus or minus button clicked")
            # Toggle the symbol visibility
            # self.isPlusSymbolVisible = not self.isPlusSymbolVisible
            # self.update()
            self.toggleContainerExpansion()
        elif self.typeTextItem.hasFocus() and not self.typeTextItem.contains(event.pos()):
            self.typeTextItem.clearFocus()
        elif not self.typeTextItem.contains(event.pos()):
            self.typeTextItem.deselectText()
        else:
            super().mousePressEvent(event)

    def getItemAttributeValues(self):
        return {
            "Container Sequence ID": self.containerSequenceId,
            "Container Name": self.containerName,
            "Container Type": self.containerType
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
        self.statusColor =  QColor(0, 255, 0)
        self.update()
    
    def loadImageWithQuality(self, path, size):
        image = QImage(path)
        if not image.isNull():
            return QPixmap.fromImage(image.scaled(size, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        return QPixmap()
    
    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange and self.scene():
            if hasattr(self, 'itemMoved') and callable(self.itemMoved):
                self.itemMoved()
        return super().itemChange(change, value)
    
    def toggleContainerExpansion(self):
        if self.isPlusSymbolVisible:
            # Expand
            self.isPlusSymbolVisible = False
            self.showContainerBox()
        else:
            # Collapse
            self.isPlusSymbolVisible = True
            self.hideContainerBox()
        self.update()
        
    def showContainerBox(self):
        if not self.containerBox:
            rect = QRectF(0, 0, self.width, 100)  # Example height for the expanded box
            self.containerBox = AssetsContainerRectangleBox(rect, self)
            self.updateContainerBoxPosition()
            self.scene().addItem(self.containerBox)

    def hideContainerBox(self):
        if self.containerBox:
            self.scene().removeItem(self.containerBox)
            self.containerBox = None
    
    def updateContainerBoxPosition(self):
        if self.containerBox:
            containerBottomLeft = self.pos() + QPointF(-self.width / 2, self.boundingRect().height() / 2)
            containerBoxPosition = containerBottomLeft + QPointF(0, self.height / 2)
            self.containerBox.setPos(containerBoxPosition)