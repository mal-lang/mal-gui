from __future__ import annotations
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, QPointF, QLineF
from PySide6.QtGui import QBrush, QColor, QPen, QPainterPath, QPainterPathStroker
from PySide6.QtWidgets import (
    QGraphicsLineItem,
    QGraphicsTextItem,
    QGraphicsRectItem,
    QGraphicsItemGroup,
)

if TYPE_CHECKING:
    from maltoolbox.language import LanguageGraphAssociation
    from .model_scene import ModelScene
    from .object_explorer import AssetItem, AttackerItem, MetaDetectorItem


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

    def delete(self):
        pass


class AssociationConnectionItem(IConnectionItem):
    def __init__(
        self,
        fieldname: str,
        start_item: AssetItem,
        end_item: AssetItem,
        scene: ModelScene,
        parent=None,
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

        # Fetch the association and the fieldnames
        lg_assoc: LanguageGraphAssociation = start_item.asset.lg_asset.associations[
            fieldname
        ]
        opposite_fieldname = lg_assoc.get_opposite_fieldname(fieldname)

        # Get left field name
        self.left_fieldname = opposite_fieldname
        # Get assoc name
        self.assoc_name = lg_assoc.name
        # Get right field name
        self.right_fieldname = fieldname

        # Create labels with background color
        self.label_assoc_left_field = self.create_label(self.left_fieldname)

        self.label_assoc_middle_name = self.create_label(self.assoc_name)

        self.label_assoc_right_field = self.create_label(self.right_fieldname)

        self.update_path()

    def create_label(self, text) -> QGraphicsItemGroup:
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
        label_group.setParentItem(self)
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
            label_assoc_left_field_pos
            - QPointF(
                self.label_assoc_left_field.boundingRect().width() / 2,
                self.label_assoc_left_field.boundingRect().height() / 2,
            )
        )

        label_assoc_middle_name_pos = self.line().pointAt(0.5)
        self.label_assoc_middle_name.setPos(
            label_assoc_middle_name_pos
            - QPointF(
                self.label_assoc_middle_name.boundingRect().width() / 2,
                self.label_assoc_middle_name.boundingRect().height() / 2,
            )
        )

        labelassoc_right_field_pos = self.line().pointAt(0.8)
        self.label_assoc_right_field.setPos(
            labelassoc_right_field_pos
            - QPointF(
                self.label_assoc_right_field.boundingRect().width() / 2,
                self.label_assoc_right_field.boundingRect().height() / 2,
            )
        )

        self.label_assoc_left_field.setVisible(
            self._scene.get_show_assoc_checkbox_status()
        )
        self.label_assoc_right_field.setVisible(
            self._scene.get_show_assoc_checkbox_status()
        )

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


class AttackerConnectionBase(IConnectionItem):
    """For both entrypoints and goals"""

    COLOR = QColor(0, 0, 0)
    LINE_STYLE = Qt.SolidLine
    ICON_TEXT = "?"

    def __init__(
        self,
        attack_step_name,
        attacker_item: AttackerItem,
        asset_item: AssetItem,
        scene: ModelScene,
        parent=None,
    ):
        super().__init__(parent)

        pen = QPen(self.COLOR, 2)
        pen.setStyle(self.LINE_STYLE)
        self.setPen(pen)
        self.setZValue(0)

        self.attacker_item = attacker_item
        self.asset_item = asset_item
        self._scene = scene
        self.attack_step_name = attack_step_name

        self.attacker_item.add_connection(self)
        self.asset_item.add_connection(self)

        self.label = self.create_label(attack_step_name)

        self.update_path()

    def create_label(self, text) -> QGraphicsItemGroup:
        label = QGraphicsTextItem(self.ICON_TEXT + " " + text)
        label.setDefaultTextColor(Qt.black)

        rect = label.boundingRect()
        bg = QGraphicsRectItem(rect)
        bg.setBrush(QBrush(QColor(255, 255, 255, 200)))
        bg.setPen(Qt.NoPen)

        group = self._scene.createItemGroup([bg, label])
        group.setParentItem(self)
        group.setZValue(1)
        return group

    def create_icon(self, text) -> QGraphicsTextItem:
        icon = QGraphicsTextItem(text)
        icon.setDefaultTextColor(self.COLOR)
        icon.setParentItem(self)
        icon.setZValue(1)
        return icon

    def update_path(self):
        start_pos = self.attacker_item.sceneBoundingRect().center()
        end_pos = self.asset_item.sceneBoundingRect().center()
        self.setLine(QLineF(start_pos, end_pos))

        # label in the middle
        mid = self.line().pointAt(0.5)
        self.label.setPos(
            mid
            - QPointF(
                self.label.boundingRect().width() / 2,
                self.label.boundingRect().height() / 2,
            )
        )

    def remove_labels(self):
        self._scene.removeItem(self.label)

    def restore_labels(self):
        self._scene.addItem(self.label)

    def delete(self):
        self.remove_labels()
        self._scene.removeItem(self)


class EntrypointConnectionItem(AttackerConnectionBase):
    COLOR = QColor(255, 0, 0)
    LINE_STYLE = Qt.SolidLine
    ICON_TEXT = "💣"


class GoalConnectionItem(AttackerConnectionBase):
    COLOR = QColor(255, 0, 0)
    LINE_STYLE = Qt.DashLine
    ICON_TEXT = "🏁"


class MetaDetectorConnectionItem(IConnectionItem):
    COLOR = QColor(255, 165, 0)

    def __init__(
        self,
        meta_detector_item: MetaDetectorItem,
        asset_item: AssetItem,
        scene: ModelScene,
        label_value: int = 1,
        parent=None,
    ):
        super().__init__(parent)

        pen = QPen(self.COLOR, 2)
        self.setPen(pen)
        self.setZValue(0)
        self.setFlag(QGraphicsLineItem.ItemIsSelectable, True)

        self.meta_detector_item = meta_detector_item
        self.asset_item = asset_item
        self._scene = scene
        self.label_value = int(label_value)

        self.meta_detector_item.add_connection(self)
        self.asset_item.add_connection(self)

        self.label = self.create_label(str(self.label_value))

        self.update_path()

    def create_label(self, text) -> QGraphicsItemGroup:
        self.label_text = QGraphicsTextItem(text)
        self.label_text.setDefaultTextColor(Qt.black)

        rect = self.label_text.boundingRect()
        self.label_background = QGraphicsRectItem(rect)
        self.label_background.setBrush(QBrush(QColor(255, 255, 255, 200)))
        self.label_background.setPen(Qt.NoPen)

        label_group = self._scene.createItemGroup(
            [self.label_background, self.label_text]
        )
        label_group.setParentItem(self)
        label_group.setZValue(1)
        return label_group

    def set_label_value(self, label_value: int):
        self.label_value = int(label_value)
        self.meta_detector_item.connected_asset_labels[
            self.asset_item.asset.name
        ] = self.label_value
        self.label_text.setPlainText(str(self.label_value))
        self.label_background.setRect(self.label_text.boundingRect())
        self.update_path()

    def get_item_attribute_values(self) -> dict[str, dict]:
        return {
            "type": {"value": "Meta Detector Connection", "editable": False},
            "from": {"value": self.meta_detector_item.name, "editable": False},
            "to": {"value": self.asset_item.asset.name, "editable": False},
            "label": {"value": self.label_value, "editable": True},
        }

    def set_item_attribute_value(self, attr_name, new_value_str) -> None:
        if attr_name != "label":
            raise AttributeError(f"{attr_name} is not editable")
        try:
            label_value = int(new_value_str)
        except ValueError:
            self.label_text.setPlainText(str(self.label_value))
            return
        self.set_label_value(label_value)

    def update_path(self):
        start_pos = self.meta_detector_item.sceneBoundingRect().center()
        end_pos = self.asset_item.sceneBoundingRect().center()
        self.setLine(QLineF(start_pos, end_pos))
        mid = self.line().pointAt(0.5)
        self.label.setPos(
            mid
            - QPointF(
                self.label.boundingRect().width() / 2,
                self.label.boundingRect().height() / 2,
            )
        )

    def shape(self):
        # Make the line easier to right-click than the visual 2px stroke.
        path = QPainterPath()
        path.moveTo(self.line().p1())
        path.lineTo(self.line().p2())

        stroker = QPainterPathStroker()
        stroker.setWidth(12)
        return stroker.createStroke(path)

    def remove_labels(self):
        self._scene.removeItem(self.label)

    def restore_labels(self):
        self._scene.addItem(self.label)

    def delete(self):
        self.meta_detector_item.remove_connection(self)
        self.asset_item.remove_connection(self)
        self.remove_labels()
        self._scene.removeItem(self)
