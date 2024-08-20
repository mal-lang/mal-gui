from PySide6.QtCore import Qt, QPointF, QLineF
from PySide6.QtGui import QBrush, QColor
from PySide6.QtWidgets import QGraphicsLineItem, QGraphicsTextItem, QGraphicsRectItem, QGraphicsItemGroup

class ConnectionItem(QGraphicsLineItem):
    def __init__(
        self,
        selectedAssociationText,
        startItem,
        endItem,
        scene,
        parent = None
    ):
        super().__init__(parent)
        
        self.setZValue(0)  # Ensure connection items are behind rect items
        
        self.showAssociationFlag = False
        
        self.startItem = startItem
        self.endItem = endItem
        self.scene = scene
        
        self.startItem.addConnection(self)
        self.endItem.addConnection(self)
        
        if self.startItem.assetType != 'Attacker' and self.endItem.assetType != 'Attacker':
        
            self.associationDetails = selectedAssociationText.split("-->")
            assocLeftField = self.associationDetails[0]
            assocMiddleName = self.associationDetails[1]
            assocRightField = self.associationDetails[2]


            # Create labels with background color
            self.labelAssocLeftField = self.createLabel(assocLeftField.split(".")[1])
            self.labelAssocMiddleName = self.createLabel(assocMiddleName)
            self.labelAssocRightField = self.createLabel(assocRightField.split(".")[1])
        
        else:
            
            #Need to check who is attacker and get the name of target and attackStep Name
            # Assumption is Both are not 'Attacker'
            if self.startItem.assetType == 'Attacker':
                attacker = self.startItem.attackerAttachment
                target = str(self.endItem.assetName)
            else:
                attacker = self.endItem.attackerAttachment
                target = str(self.startItem.assetName)
            
            #selectedAssociationText is representing 'AttackStep' name
            attacker.entry_points.append(target + ' -> ' + selectedAssociationText)
            self.labelAssocLeftField = self.createLabel("")
            self.labelAssocMiddleName = self.createLabel(selectedAssociationText)
            self.labelAssocRightField = self.createLabel("")
        
        
        
        self.updatePath()

    def createLabel(self, text):
        # Create the label
        label = QGraphicsTextItem(text)
        label.setDefaultTextColor(Qt.black)

        # Create a white background for the label
        rect = label.boundingRect()
        labelBackground = QGraphicsRectItem(rect)
        labelBackground.setBrush(QBrush(QColor(255, 255, 255, 200)))  # Semi-transparent white background
        labelBackground.setPen(Qt.NoPen)

        # Create a group to hold the label and its background
        labelGroup = self.scene.createItemGroup([labelBackground, label])
        labelGroup.setZValue(1)  # Ensure labels are above the line

        return labelGroup

    def updatePath(self):
        """
        Draws a straight line from the start to end items and updates label positions.
        """
        self.startPos = self.startItem.sceneBoundingRect().center()
        self.endPos = self.endItem.sceneBoundingRect().center()
        self.setLine(QLineF(self.startPos, self.endPos))
        
        # Calculate offsets to position labels outside the bounding rectangles
        start_rect = self.startItem.sceneBoundingRect()
        end_rect = self.endItem.sceneBoundingRect()
        
        labelAssocLeftFieldPos = self.line().pointAt(0.2)
        self.labelAssocLeftField.setPos(labelAssocLeftFieldPos - QPointF(self.labelAssocLeftField.boundingRect().width() / 2, self.labelAssocLeftField.boundingRect().height() / 2))

        labelAssocMiddleNamePos = self.line().pointAt(0.5)
        self.labelAssocMiddleName.setPos(labelAssocMiddleNamePos - QPointF(self.labelAssocMiddleName.boundingRect().width() / 2, self.labelAssocMiddleName.boundingRect().height() / 2))

        labelAssocRightFieldPos = self.line().pointAt(0.8)
        self.labelAssocRightField.setPos(labelAssocRightFieldPos - QPointF(self.labelAssocRightField.boundingRect().width() / 2, self.labelAssocRightField.boundingRect().height() / 2))
        
        # print("isAssociationVisibilityChecked = "+ str(self.isAssociationVisibilityChecked))
        
        self.labelAssocLeftField.setVisible(self.scene.getShowAssociationCheckBoxStatus())
        self.labelAssocRightField.setVisible(self.scene.getShowAssociationCheckBoxStatus())

    def calculateOffset(self, rect, label_pos, angle):
        """
        Calculate the offset to position the label outside the bounding rectangle.
        """
        offset_distance = 10  # Distance to move the label outside the rectangle
        offset = QPointF()
        angle_radians = angle * 3.14159 / 180  # Convert angle to radians
        
        if angle < 90 or angle > 270:
            offset.setX(rect.width() / 2 + offset_distance)
        else:
            offset.setX(-(rect.width() / 2 + offset_distance))
        
        if angle < 180:
            offset.setY(rect.height() / 2 + offset_distance)
        else:
            offset.setY(-(rect.height() / 2 + offset_distance))
        
        return offset
    
    # def setShowAssocitaions(self,isEnabled):
    #     print("Toggled show/hide association labels-->"+ str(isEnabled))
    #     # self.labelAssocLeftField.setVisible(isEnabled)
    #     # self.labelAssocRightField.setVisible(isEnabled)
    #     self.isAssociationVisibilityChecked = isEnabled 
    #     self.updatePath()
        
    def removeLabels(self):
        self.scene.removeItem(self.labelAssocLeftField)
        self.scene.removeItem(self.labelAssocMiddleName)
        self.scene.removeItem(self.labelAssocRightField)
    
    def restoreLabels(self):
        self.scene.addItem(self.labelAssocLeftField)
        self.scene.addItem(self.labelAssocMiddleName)
        self.scene.addItem(self.labelAssocRightField)

    def delete(self):
        self.removeLabels()
        self.scene.removeItem(self)
        
