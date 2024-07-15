from PySide6.QtGui import QUndoCommand

class CopyCommand(QUndoCommand):
    def __init__(self, scene, items, clipboard, parent=None):
        super().__init__(parent)
        self.scene = scene
        self.items = items
        self.clipboard = clipboard

    def redo(self):
        self.cutItemFlag = False
        serializedData = self.scene.serializeGraphicsItems(self.items, self.cutItemFlag)
        self.clipboard.clear()
        self.clipboard.setText(serializedData) 

    def undo(self):
        self.clipboard.clear()