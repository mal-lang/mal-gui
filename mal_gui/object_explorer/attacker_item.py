from PySide6.QtGui import QColor
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QGraphicsItem
from shiboken6 import isValid

from .item_base import ItemBase

class AttackerItem(ItemBase):
    # Starting Sequence Id with normal start at 100 (randomly taken)

    def __init__(
            self,
            name: str,
            image_path: str,
            entry_points=None,
            parent=None,
        ):

        self.entry_points: list[str] = entry_points or []
        self.name = name
        self.attacker_toggle_state = False

        self.timer = QTimer()
        self.status_color = QColor(0, 255, 0)
        self.attacker_toggle_state = False
        self.timer.timeout.connect(self.update_status_color)
        self.timer.start(500)

        super().__init__('Attacker', image_path, parent)

    def update_type_text_item_position(self):
        super().update_type_text_item_position()
        # For Attacker make the background of type As Red
        self.asset_type_background_color = QColor(255, 0, 0)  # Red

    def update_name(self):
        """Update the name of the attacker"""
        super().update_name()
        self.name = self.title

    def get_item_attribute_values(self):
        return {
            "Attacker name": self.name,
            "Entry points": self.entry_points,
        }

    def update_status_color(self):
        # Object may already be deleted on C++ side
        if not isValid(self):
            return

        # Still check if removed from scene
        if self.scene() is None:
            if self.timer.isActive():
                self.timer.stop()
            return

        self.attacker_toggle_state = not self.attacker_toggle_state
        if self.attacker_toggle_state:
            self.status_color = QColor(0, 255, 0)  # Green
        else:
            self.status_color = QColor(255, 0, 0)  # Red
        self.update()

    def itemChange(self, change, value):
        """Override to stop timer when item is removed from scene"""
        if change == QGraphicsItem.ItemSceneChange:
            if value is None and self.timer.isActive():
                self.timer.stop()
        return super().itemChange(change, value)

    def serialize(self):
        return {
            'title': self.title,
            'image_path': self.image_path,
            'type': 'asset',
            'object': self.entry_points
        }
