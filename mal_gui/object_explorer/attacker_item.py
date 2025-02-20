from __future__ import annotations
from typing import TYPE_CHECKING

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

from .editable_text_item import EditableTextItem
from .item_base import ItemBase

if TYPE_CHECKING:
    from maltoolbox.model import ModelAsset, AttackerAttachment
    from ..connection_item import IConnectionItem

class AttackerItem(ItemBase):
    # Starting Sequence Id with normal start at 100 (randomly taken)

    def __init__(
            self,
            attacker: AttackerAttachment,
            image_path: str,
            parent=None,
        ):

        self.attacker = attacker
        self.attacker_toggle_state = False
        super().__init__('Attacker', image_path, parent)

    def update_type_text_item_position(self):
        super().update_type_text_item_position()
        # For Attacker make the background of type As Red
        self.asset_type_background_color = QColor(255, 0, 0) #Red

    def update_name(self):
        """Update the name of the attacker"""
        super().update_name()
        self.attacker.name = self.title

    def get_item_attribute_values(self):
        return {
            "Attacker ID": self.attacker.id,
            "Attacker name": self.attacker.name,
        }

    def update_status_color(self):
        self.attacker_toggle_state = not self.attacker_toggle_state
        if self.attacker_toggle_state:
            self.status_color =  QColor(0, 255, 0) # Green
        else:
            self.status_color =  QColor(255, 0, 0) # Red
        self.update()

    def serialize(self):
        return {
            'title': self.title,
            'image_path': self.image_path,
            'type': 'asset',
            'object': self.attacker
        }
