from __future__ import annotations
from typing import TYPE_CHECKING
from PySide6.QtGui import QUndoCommand

if TYPE_CHECKING:
    from ..object_explorer.asset_item import AssetItem
    from ..model_scene import ModelScene

class MoveCommand(QUndoCommand):
    def __init__(
            self,
            scene: ModelScene,
            items: list,
            start_positions,
            end_positions,
            parent=None
        ):
        super().__init__(parent)
        self.scene = scene
        self.items = items
        self.start_positions = start_positions
        self.end_positions = end_positions

    def redo(self):
        """Perform move"""
        print("Move Redo")
        for item in self.items:
            item.setPos(self.end_positions[item])
            self.update_connections(item)

    def undo(self):
        """Undo move"""
        print("Move Undo")
        for item in self.items:
            item.setPos(self.start_positions[item])
            self.update_connections(item)

    def update_connections(self, item: AssetItem):
        """Redraw connecting lines"""
        if hasattr(item, 'connections'):
            for connection in item.connections:
                connection.update_path()
