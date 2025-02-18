from __future__ import annotations
from typing import TYPE_CHECKING
from PySide6.QtGui import QUndoCommand

if TYPE_CHECKING:
    from ..model_scene import ModelScene
    from ..object_explorer.asset_item import AssetItem

class CopyCommand(QUndoCommand):
    def __init__(self, scene: ModelScene, items: list[AssetItem], clipboard, parent=None):
        super().__init__(parent)
        self.scene = scene
        self.items = items
        self.clipboard = clipboard

    def redo(self):
        self.cut_item_flag = False
        serialized_data = \
            self.scene.serialize_graphics_items(self.items, self.cut_item_flag)
        self.clipboard.clear()
        self.clipboard.setText(serialized_data)

    def undo(self):
        self.clipboard.clear()
