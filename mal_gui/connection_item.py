from __future__ import annotations
from typing import TYPE_CHECKING, Any

from PySide6.QtCore import Qt, QPointF, QLineF
from PySide6.QtGui import QBrush, QColor,QPen
from PySide6.QtWidgets import (
    QGraphicsLineItem,
    QGraphicsTextItem,
    QGraphicsRectItem,
)

if TYPE_CHECKING:
    from maltoolbox.language import LanguageGraphAssociation
    from .model_scene import ModelScene
    from .object_explorer import AssetItem, AttackerItem

class IConnectionItem(QGraphicsLineItem):
    """'interface' for Connection Item"""
    start_item: AssetItem
    end_item: AssetItem
    association_details: list[str]

    def create_label(self, text):
        pass

    def update_path(self):
        pass

    def remove_labels(self):
        pass

    def restore_labels(self):
        pass


class AssociationConnectionItem(IConnectionItem):
    def __init__(
        self,
        fieldname: str,
        start_item: AssetItem,
        end_item: AssetItem,
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

        self.start_item.add_connection(self)
        self.end_item.add_connection(self)

        if (
            self.start_item.asset_type != 'Attacker'
            and self.end_item.asset_type != 'Attacker'
        ):
            # Fetch the association and the fieldnames
            lg_assoc: LanguageGraphAssociation = (
                start_item.asset.lg_asset.associations[fieldname]
            )
            opposite_fieldname = lg_assoc.get_opposite_fieldname(fieldname)

            # Get left field name
            self.left_fieldname = opposite_fieldname
            # Get assoc name
            self.assoc_name = lg_assoc.name
            # Get right field name
            self.right_fieldname = fieldname

            # Create labels with background color
            self.label_assoc_left_field = \
                self.create_label(self.left_fieldname)

            self.label_assoc_middle_name = \
                self.create_label(self.assoc_name)

            self.label_assoc_right_field = \
                self.create_label(self.right_fieldname)

        else:
            # Need to check who is attacker and get
            # the name of target and attackStep Name.
            # Assumption is Both are not 'Attacker'.
            if self.start_item.asset_type == 'Attacker':
                attacker = self.start_item.attackerAttachment
                target = str(self.end_item.asset_name)
            else:
                attacker = self.end_item.attackerAttachment
                target = str(self.start_item.asset_name)

            #selected_assoc_text is representing 'AttackStep' name
            entry_point_text = target + ' -> ' + selected_assoc_text
            attacker.entry_points.append(entry_point_text)
            self.label_assoc_left_field = self.create_label("")
            self.label_assoc_middle_name = self.create_label(selected_assoc_text)
            self.label_assoc_right_field = self.create_label("")

        self.update_path()

    def create_label(self, text):
        """Create the connection label"""
        label = QGraphicsTextItem(text)
        label.setDefaultTextColor(Qt.black)

        # Create a white background for the label
        rect = label.boundingRect()
        # Semi-transparent white background
        label_background = QGraphicsRectItem(rect)
        label_background.setBrush(QBrush(QColor(255, 255, 255, 200)))
        label_background.setPen(Qt.NoPen)

        # Create a group to hold the label and its background
        label_group = self._scene.createItemGroup([label_background, label])
        label_group.setZValue(1)  # Ensure labels are above the line

        return label_group

    def update_path(self):
        """
        Draws a straight line from the start to end
        items and updates label positions.
        """
        start_pos = self.start_item.sceneBoundingRect().center()
        end_pos = self.end_item.sceneBoundingRect().center()
        self.setLine(QLineF(start_pos, end_pos))

        label_assoc_left_field_pos = self.line().pointAt(0.2)
        self.label_assoc_left_field.setPos(
            label_assoc_left_field_pos - QPointF(
                self.label_assoc_left_field.boundingRect().width() / 2,
                self.label_assoc_left_field.boundingRect().height() / 2
            )
        )

        label_assoc_middle_name_pos = self.line().pointAt(0.5)
        self.label_assoc_middle_name.setPos(
            label_assoc_middle_name_pos - QPointF(
                self.label_assoc_middle_name.boundingRect().width() / 2,
                self.label_assoc_middle_name.boundingRect().height() / 2
            )
        )

        labelassoc_right_field_pos = self.line().pointAt(0.8)
        self.label_assoc_right_field.setPos(
            labelassoc_right_field_pos - QPointF(
                self.label_assoc_right_field.boundingRect().width() / 2,
                self.label_assoc_right_field.boundingRect().height() / 2
            )
        )

        self.label_assoc_left_field.setVisible(
            self._scene.get_show_assoc_checkbox_status())
        self.label_assoc_right_field.setVisible(
            self._scene.get_show_assoc_checkbox_status())

    def calculate_offset(self, rect, label_pos, angle):
        """Calculate the offset to position the label
        outside the bounding rectangle."""

        # Distance to move the label outside the rectangle
        offset_distance = 10
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

    def remove_labels(self):
        """Remove the labels from a connection item"""
        self._scene.removeItem(self.label_assoc_left_field)
        self._scene.removeItem(self.label_assoc_middle_name)
        self._scene.removeItem(self.label_assoc_right_field)

    def restore_labels(self):
        """Undo delete of connection item"""
        self._scene.addItem(self.label_assoc_left_field)
        self._scene.addItem(self.label_assoc_middle_name)
        self._scene.addItem(self.label_assoc_right_field)

    def delete(self):
        """Delete connection item"""
        self.remove_labels()
        self._scene.removeItem(self)


class EntrypointConnectionItem(IConnectionItem):
    def __init__(
        self,
        attack_step_name,
        attacker_item: AttackerItem,
        asset_item: AssetItem,
        scene: ModelScene,
        parent = None
    ):
        super().__init__(parent)

        pen = QPen(QColor(255, 0, 0), 2)  # Red color with 2-pixel thickness
        self.setPen(pen)
        self.setZValue(0)  # Ensure connection items are behind rect items

        self.attacker_item = attacker_item
        self.asset_item = asset_item
        self._scene = scene

        self.attacker_item.add_connection(self)
        self.asset_item.add_connection(self)
        self.attack_step_name = attack_step_name
        self.label_entrypoint = self.create_label(attack_step_name)

    def create_label(self, text):
        # Create the label
        label = QGraphicsTextItem(text)
        label.setDefaultTextColor(Qt.black)

        # Create a white background for the label
        rect = label.boundingRect()
        label_background = QGraphicsRectItem(rect)
        label_background.setBrush(QBrush(QColor(255, 255, 255, 200)))
        label_background.setPen(Qt.NoPen)

        # Create a group to hold the label and its background
        label_group = self._scene.createItemGroup([label_background, label])
        label_group.setZValue(1)  # Ensure labels are above the line

        return label_group

    def update_path(self):
        """Draw straight line from start to end items
        and updates label positions."""

        start_pos = self.attacker_item.sceneBoundingRect().center()
        end_pos = self.asset_item.sceneBoundingRect().center()
        self.setLine(QLineF(start_pos, end_pos))

        label_entrypoints_pos = self.line().pointAt(0.5)
        self.label_entrypoint.setPos(
            label_entrypoints_pos - QPointF(
                self.label_entrypoint.boundingRect().width() / 2,
                self.label_entrypoint.boundingRect().height() / 2
            )
        )

    def remove_labels(self):
        self._scene.removeItem(self.label_entrypoint)

    def restore_labels(self):
        self._scene.addItem(self.label_entrypoint)
