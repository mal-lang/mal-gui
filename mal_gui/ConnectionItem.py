from __future__ import annotations
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, QPointF, QLineF
from PySide6.QtGui import QBrush, QColor,QPen
from PySide6.QtWidgets import (
    QGraphicsLineItem,
    QGraphicsTextItem,
    QGraphicsRectItem,
)

if TYPE_CHECKING:
    from ModelScene import ModelScene

class IConnectionItem(QGraphicsLineItem):
    def createLabel(self, text):
        pass

    def updatePath(self):
        pass

    def removeLabels(self):
        pass

    def restoreLabels(self):
        pass


class AssociationConnectionItem(IConnectionItem):
    def __init__(
        self,
        selected_assoc_text: str,
        start_item,
        end_item,
        scene: ModelScene,
        parent = None
    ):
        super().__init__(parent)

        pen = QPen(QColor(0, 255, 0), 2)  # Green color with 2-pixel thickness
        self.setPen(pen)
        self.setZValue(0)  # Ensure connection items are behind rect items

        self.show_assoc_flag = False
        self.start_item = start_item
        self.end_item = end_item
        self._scene = scene

        self.start_item.addConnection(self)
        self.end_item.addConnection(self)

        if self.start_item.assetType != 'Attacker' and self.end_item.assetType != 'Attacker':

            self.associationDetails = selected_assoc_text.split("-->")
            assocLeftField = self.associationDetails[0]
            assocMiddleName = self.associationDetails[1]
            assocRightField = self.associationDetails[2]

            # Create labels with background color
            self.labelAssocLeftField = self.createLabel(assocLeftField.split(".")[1])
            self.labelAssocMiddleName = self.createLabel(assocMiddleName)
            self.labelAssocRightField = self.createLabel(assocRightField.split(".")[1])

        else:
            #Need to check who is attacker and get
            # the name of target and attackStep Name.
            # Assumption is Both are not 'Attacker'.
            if self.start_item.assetType == 'Attacker':
                attacker = self.start_item.attackerAttachment
                target = str(self.end_item.assetName)
            else:
                attacker = self.end_item.attackerAttachment
                target = str(self.start_item.assetName)

            #selected_assoc_text is representing 'AttackStep' name
            attacker.entry_points.append(target + ' -> ' + selected_assoc_text)
            self.labelAssocLeftField = self.createLabel("")
            self.labelAssocMiddleName = self.createLabel(selected_assoc_text)
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
        labelGroup = self._scene.createItemGroup([labelBackground, label])
        labelGroup.setZValue(1)  # Ensure labels are above the line

        return labelGroup

    def updatePath(self):
        """
        Draws a straight line from the start to end items and updates label positions.
        """
        self.startPos = self.start_item.sceneBoundingRect().center()
        self.endPos = self.end_item.sceneBoundingRect().center()
        self.setLine(QLineF(self.startPos, self.endPos))

        labelAssocLeftFieldPos = self.line().pointAt(0.2)
        self.labelAssocLeftField.setPos(labelAssocLeftFieldPos - QPointF(self.labelAssocLeftField.boundingRect().width() / 2, self.labelAssocLeftField.boundingRect().height() / 2))

        labelAssocMiddleNamePos = self.line().pointAt(0.5)
        self.labelAssocMiddleName.setPos(labelAssocMiddleNamePos - QPointF(self.labelAssocMiddleName.boundingRect().width() / 2, self.labelAssocMiddleName.boundingRect().height() / 2))

        labelAssocRightFieldPos = self.line().pointAt(0.8)
        self.labelAssocRightField.setPos(labelAssocRightFieldPos - QPointF(self.labelAssocRightField.boundingRect().width() / 2, self.labelAssocRightField.boundingRect().height() / 2))

        # print("isAssociationVisibilityChecked = "+ str(self.isAssociationVisibilityChecked))

        self.labelAssocLeftField.setVisible(self._scene.get_show_assoc_checkbox_status())
        self.labelAssocRightField.setVisible(self._scene.get_show_assoc_checkbox_status())

    def calculateOffset(self, rect, label_pos, angle):
        """
        Calculate the offset to position the label outside the bounding rectangle.
        """
        offset_distance = 10  # Distance to move the label outside the rectangle
        offset = QPointF()

        if angle < 90 or angle > 270:
            offset.setX(rect.width() / 2 + offset_distance)
        else:
            offset.setX(-(rect.width() / 2 + offset_distance))

        if angle < 180:
            offset.setY(rect.height() / 2 + offset_distance)
        else:
            offset.setY(-(rect.height() / 2 + offset_distance))

        return offset

    def removeLabels(self):
        self._scene.removeItem(self.labelAssocLeftField)
        self._scene.removeItem(self.labelAssocMiddleName)
        self._scene.removeItem(self.labelAssocRightField)

    def restoreLabels(self):
        self._scene.addItem(self.labelAssocLeftField)
        self._scene.addItem(self.labelAssocMiddleName)
        self._scene.addItem(self.labelAssocRightField)

    def delete(self):
        self.removeLabels()
        self._scene.removeItem(self)


class EntrypointConnectionItem(IConnectionItem):
    def __init__(
        self,
        attackStepName,
        attackerItem,
        assetItem,
        scene: ModelScene,
        parent = None
    ):
        super().__init__(parent)

        pen = QPen(QColor(255, 0, 0), 2)  # Red color with 2-pixel thickness
        self.setPen(pen)

        self.setZValue(0)  # Ensure connection items are behind rect items

        self.attackerItem = attackerItem
        self.assetItem = assetItem
        self._scene = scene

        self.attackerItem.addConnection(self)
        self.assetItem.addConnection(self)
        self.labelEntrypoint = self.createLabel(attackStepName)

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
        labelGroup = self._scene.createItemGroup([labelBackground, label])
        labelGroup.setZValue(1)  # Ensure labels are above the line

        return labelGroup

    def updatePath(self):
        """
        Draws a straight line from the start to end items and updates label positions.
        """
        self.startPos = self.attackerItem.sceneBoundingRect().center()
        self.endPos = self.assetItem.sceneBoundingRect().center()
        self.setLine(QLineF(self.startPos, self.endPos))

        labelEntrypointPos = self.line().pointAt(0.5)
        self.labelEntrypoint.setPos(
            labelEntrypointPos - QPointF(
                self.labelEntrypoint.boundingRect().width() / 2,
                self.labelEntrypoint.boundingRect().height() / 2
            )
        )

    def removeLabels(self):
        self._scene.removeItem(self.labelEntrypoint)

    def restoreLabels(self):
        self._scene.addItem(self.labelEntrypoint)
