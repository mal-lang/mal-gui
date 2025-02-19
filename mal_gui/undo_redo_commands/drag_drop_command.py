from __future__ import annotations
from typing import TYPE_CHECKING

from PySide6.QtGui import QUndoCommand
from ..object_explorer import AssetItem, AttackerItem

if TYPE_CHECKING:
    from mal_gui.model_scene import ModelScene

class DragDropCommand(QUndoCommand):
    def __init__(self, scene: ModelScene, item, parent=None):
        super().__init__(parent)
        self.scene = scene
        self.item = item

    def redo(self):
        """Perform drag and drop"""
        print("REDO DROP!")
        self.scene.addItem(self.item)

        #Update the Object Explorer when number of items change
        self.scene.main_window.update_childs_in_object_explorer_signal.emit()

    def undo(self):
        """Undo drag and drop"""
        self.scene.removeItem(self.item)
        print("UNDO DROP!")

        if isinstance(self.item, AssetItem):
            self.scene.model.remove_asset(self.item.asset)
        elif isinstance(self.item, AttackerItem):
            self.scene.model.remove_attacker(self.item.attacker)

        #Update the Object Explorer when number of items change
        self.scene.main_window.update_childs_in_object_explorer_signal.emit()
