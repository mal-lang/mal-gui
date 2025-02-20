from __future__ import annotations
from typing import TYPE_CHECKING

from PySide6.QtGui import QUndoCommand
from PySide6.QtCore import QPointF

if TYPE_CHECKING:
    from mal_gui.model_scene import ModelScene

class DragDropAssetCommand(QUndoCommand):
    def __init__(
        self,
        scene: ModelScene,
        asset_type: str,
        position: QPointF,
        name = None,
        parent=None,
    ):
        """
        The command needs to store everything that is
        needed to create/remove an asset and its item
        """
        super().__init__(parent)

        self.scene = scene
        self.item = None
        self.asset_type = asset_type
        self.position = position
        self.name = name

    def redo(self):
        """Perform drag and drop"""
        print("REDO DROP!")

        # If it is an 'actual' redo, we need to add the same asset again
        if self.item:
            # Create asset from previous deleted asset
            self.item = self.scene.recreate_asset(
                self.item, self.position
            )
        else:
            # Create/add asset from scratch
            self.item = self.scene.create_asset(
                self.asset_type, self.position, self.name
            )

        #Update the Object Explorer when number of items change
        self.scene.main_window.update_childs_in_object_explorer_signal.emit()

    def undo(self):
        """Undo drag and drop"""

        if self.item is None:
            print("Asset does not exist - nothing to remove while undoing")
        else:
            print("Removing asset item")
            self.scene.remove_asset(self.item)

        # Update the Object Explorer when number of items change
        self.scene.main_window.update_childs_in_object_explorer_signal.emit()


class DragDropAttackerCommand(QUndoCommand):
    def __init__(self, scene: ModelScene, position: QPointF, parent=None):
        """We need all info required to create/remove attacker"""
        super().__init__(parent)
        self.scene = scene
        self.position = position
        self.item = None

    def redo(self):
        """Perform drag and drop"""
        print("REDO DROP!")

        if self.item:
            # Create attacker from previous deleted attacker
            self.item = self.scene.create_attacker(
                self.item.pos(),
                name=self.item.attacker.name,
                attacker_id=self.item.attacker.id
            )
        else:
            # Create attacker from scratch
            self.item = self.scene.create_attacker(self.position)

        #Update the Object Explorer when number of items change
        self.scene.main_window.update_childs_in_object_explorer_signal.emit()

    def undo(self):
        """Undo drag and drop"""

        if self.item is not None:
            self.scene.remove_attacker(self.item)

        # Update the Object Explorer when number of items change
        self.scene.main_window.update_childs_in_object_explorer_signal.emit()
