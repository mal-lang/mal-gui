from PySide6.QtGui import QUndoCommand, QUndoStack
from PySide6.QtCore import QPointF
from PySide6.QtWidgets import QApplication

class PasteCommand(QUndoCommand):
    def __init__(self, scene, position,clipboard, parent=None):
        super().__init__(parent)
        self.scene = scene
        self.position = position
        self.pastedNode = None
        self.clipboard = clipboard

    def redo(self):
        print("\nPaste Redo is Called")
        serializedData = self.clipboard.text()
        print("\nSerializedData = "+ str(len(serializedData)))
        print("\nSerializedData = "+ str(serializedData))
        if serializedData:
            self.pastedNode = self.scene.deserializeGraphicsItem(serializedData)
            if self.pastedNode:
                print("Redo - Pasted Node found")
                self.scene.addItem(self.pastedNode)
                if self.position:
                    self.pastedNode.setPos(self.position)

    def undo(self):
        print("\nPaste Undo is Called")
        if self.pastedNode:
            print("Undo - Pasted Node found")
            self.scene.removeItem(self.pastedNode)
            self.pastedNode = None