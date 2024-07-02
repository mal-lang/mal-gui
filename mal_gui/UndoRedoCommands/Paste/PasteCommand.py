from PySide6.QtGui import QUndoCommand, QUndoStack
from PySide6.QtCore import QPointF
from PySide6.QtWidgets import QApplication

class PasteCommand(QUndoCommand):
    def __init__(self, scene, position,clipboard, parent=None):
        super().__init__(parent)
        self.scene = scene
        self.position = position
        self.pastedAsset= None
        self.clipboard = clipboard

    def redo(self):
        print("\nPaste Redo is Called")
        serializedData = self.clipboard.text()
        print("\nSerializedData = "+ str(len(serializedData)))
        print("\nSerializedData = "+ str(serializedData))
        if serializedData:
            self.pastedAsset = self.scene.deserializeGraphicsItem(serializedData)
            if self.pastedAsset:
                print("Redo - Pasted Asset found")
                self.scene.addItem(self.pastedAsset)
                if self.position:
                    self.pastedAsset.setPos(self.position)

    def undo(self):
        print("\nPaste Undo is Called")
        if self.pastedAsset:
            print("Undo - Pasted Asset found")
            self.scene.removeItem(self.pastedAsset)
            self.pastedAsset = None