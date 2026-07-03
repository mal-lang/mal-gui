from PySide6.QtGui import QColor
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QGraphicsItem
from shiboken6 import isValid

from malsim import policies

from .item_base import ItemBase

ALLOWED_POLICIES = [
    policies.PassiveAgent,
    policies.BreadthFirstAttacker,
    policies.DepthFirstAttacker,
    policies.RandomAgent,
    policies.TTCSoftMinAttacker,
]
POLICY_NAME_TO_CLASS = {cls.__name__: cls for cls in ALLOWED_POLICIES}


def resolve_policy(policy_name: str | None):
    if not policy_name:
        return policies.PassiveAgent
    return POLICY_NAME_TO_CLASS.get(policy_name, policies.PassiveAgent)


class AttackerItem(ItemBase):
    TITLE = "Attacker"
    HEADER_COLOR = (255, 0, 0)
    ITEM_KIND = "attacker"

    # Starting Sequence Id with normal start at 100 (randomly taken)

    def __init__(
        self,
        name: str,
        image_path: str,
        entry_points=None,
        goals=None,
        policy=None,
        parent=None,
    ):

        # Scenario data may come in as sets; normalize to lists for GUI ops.
        self.entry_points: list[str] = list(entry_points) if entry_points else []
        self.policy = policy or policies.PassiveAgent
        self.goals: list[str] = list(goals) if goals else []
        self.name = name
        self.attacker_toggle_state = False

        self.timer = QTimer()
        self.status_color = QColor(0, 255, 0)
        self.attacker_toggle_state = False
        self.timer.timeout.connect(self.update_status_color)
        self.timer.start(500)

        super().__init__(self.TITLE, image_path, parent)

    def update_type_text_item_position(self):
        super().update_type_text_item_position()
        self.asset_type_background_color = QColor(*self.HEADER_COLOR)

    def update_name(self):
        """Update the name of the attacker"""
        super().update_name()
        self.name = self.title

    def get_item_attribute_values(self) -> dict[str, dict]:
        return {
            "name": {"value": self.name, "editable": False},
            "entry_points": {"value": self.entry_points, "editable": False},
            "goals": {"value": self.goals, "editable": False},
            "policy": {
                "value": self.policy.__name__,
                "editable": True,
                "type": "enum",
                "choices": [cls.__name__ for cls in ALLOWED_POLICIES],
            },
        }

    def set_item_attribute_value(self, attr_name, new_value_str) -> None:
        if attr_name == "policy":
            if new_value_str not in POLICY_NAME_TO_CLASS:
                raise ValueError(f"Invalid policy: {new_value_str}")
            print("Change policy to ", new_value_str)
            self.policy = POLICY_NAME_TO_CLASS[new_value_str]
            return
        raise AttributeError(f"{attr_name} is not editable")

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
            "title": self.title,
            "image_path": self.image_path,
            "type": self.ITEM_KIND,
            "object": self.entry_points,
        }
