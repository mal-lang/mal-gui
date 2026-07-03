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
        parent=None,
    ):
        super().__init__(parent)
        self.scene = scene
        self.attacker_item = attacker_item
        self.asset_item = asset_item
        self.attack_step_name = attack_step_name
        self.connection = None
        self.step_full_name = self.asset_item.asset.name + ":" + self.attack_step_name

    def _add_step(self):
        if isinstance(self.attacker_item.entry_points, set):
            self.attacker_item.entry_points.add(self.step_full_name)
            return
        if self.step_full_name not in self.attacker_item.entry_points:
            self.attacker_item.entry_points.append(self.step_full_name)

    def _remove_step(self):
        try:
            self.attacker_item.entry_points.remove(self.step_full_name)
        except (ValueError, KeyError):
            pass

    def redo(self):
        """Create entrypoint for attacker"""
        self.connection = self.scene.add_entrypoint_connection(
            self.attack_step_name, self.attacker_item, self.asset_item
        )
        self._add_step()

    def undo(self):
        """Undo entrypoint creation"""
        if self.connection:
            self.connection.remove_labels()
            self.scene.removeItem(self.connection)

        self._remove_step()
