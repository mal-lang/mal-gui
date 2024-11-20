from __future__ import annotations
from typing import TYPE_CHECKING

from PySide6.QtGui import QUndoCommand

if TYPE_CHECKING:
    from ..ModelScene import ModelScene
class CreateEntrypointConnectionCommand(QUndoCommand):
    def __init__(
        self,
        scene: ModelScene,
        attackerItem,
        assetItem,
        attackStepName,
        parent=None
    ):
        super().__init__(parent)
        self.scene = scene
        self.attackerItem = attackerItem
        self.assetItem = assetItem
        self.attackStepName = attackStepName
        self.connection = None

    def redo(self):
        self.connection = self.scene.add_entrypoint_connection(
            self.attackStepName,
            self.attackerItem,
            self.assetItem
        )
        self.attackerItem.attackerAttachment.add_entry_point(
            self.assetItem.asset, self.attackStepName
        )

    def undo(self):
        self.connection.removeLabels()
        self.scene.removeItem(self.connection)

        self.attacker.attackerAttachment.remove_entry_point(
            self.assetItem.asset, self.attackStepName
        )
