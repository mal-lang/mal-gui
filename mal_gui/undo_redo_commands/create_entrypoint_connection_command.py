from __future__ import annotations
from typing import TYPE_CHECKING

from PySide6.QtGui import QUndoCommand

if TYPE_CHECKING:
    from ..model_scene import ModelScene
    from ..object_explorer import AttackerItem, AssetItem
class CreateEntrypointConnectionCommand(QUndoCommand):
    def __init__(
        self,
        scene: ModelScene,
        attacker_item: AttackerItem,
        asset_item: AssetItem,
        attack_step_name: str,
        parent=None
    ):
        super().__init__(parent)
        self.scene = scene
        self.attacker_item = attacker_item
        self.asset_item = asset_item
        self.attack_step_name = attack_step_name
        self.connection = None

    def redo(self):
        """Create entrypoint for attacker"""
        self.connection = self.scene.add_entrypoint_connection(
            self.attack_step_name,
            self.attacker_item,
            self.asset_item
        )
        self.attacker_item.attacker.add_entry_point(
            self.asset_item.asset, self.attack_step_name
        )

    def undo(self):
        """Undo entrypoint creation"""
        self.connection.remove_labels()
        self.scene.removeItem(self.connection)

        self.attacker_item.attacker.remove_entry_point(
            self.asset_item.asset, self.attack_step_name
        )
