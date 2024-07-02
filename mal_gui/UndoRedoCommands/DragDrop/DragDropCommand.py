from PySide6.QtGui import QUndoCommand, QUndoStack
class DragDropCommand(QUndoCommand):
    def __init__(self, scene, item, parent=None):
        super().__init__(parent)
        self.scene = scene
        self.item = item

    def redo(self):
        self.scene.addItem(self.item)

    def undo(self):
        self.scene.removeItem(self.item)