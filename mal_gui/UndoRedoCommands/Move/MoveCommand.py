from PySide6.QtGui import QUndoCommand, QUndoStack
class MoveCommand(QUndoCommand):
    def __init__(self, scene, item, startPos, endPos, parent=None):
        super().__init__(parent)
        self.scene = scene
        self.item = item
        self.startPos = startPos
        self.endPos = endPos

    def redo(self):
        print("Move Redo")
        self.item.setPos(self.endPos)
        self.updateConnections()

    def undo(self):
        print("Move Undo")
        self.item.setPos(self.startPos)
        self.updateConnections()
        
    def updateConnections(self):
        if hasattr(self.item, 'connections'):
            for connection in self.item.connections:
                connection.updatePath()