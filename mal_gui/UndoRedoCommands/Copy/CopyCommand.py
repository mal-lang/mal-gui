from PySide6.QtGui import QUndoCommand, QUndoStack

class CopyCommand(QUndoCommand):
    def __init__(self, scene, item, clipboard, parent=None):
        super().__init__(parent)
        self.scene = scene
        self.item = item
        self.clipboard = clipboard

    def redo(self):
        self.cutItemFlag = False
        serializedData = self.scene.serializeGraphicsItem(self.item, self.cutItemFlag)
        self.clipboard.clear()
        self.clipboard.setText(serializedData) 

    def undo(self):
        self.clipboard.clear()