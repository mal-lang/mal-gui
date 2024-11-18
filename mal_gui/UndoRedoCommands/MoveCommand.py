from PySide6.QtGui import QUndoCommand


class MoveCommand(QUndoCommand):
    def __init__(self, scene, items, startPositions, endPositions, parent=None):
        super().__init__(parent)
        self.scene = scene
        self.items = items
        self.startPositions = startPositions
        self.endPositions = endPositions

    def redo(self):
        print("Move Redo")
        for item in self.items:
            item.setPos(self.endPositions[item])
            self.updateConnections(item)

    def undo(self):
        print("Move Undo")
        for item in self.items:
            item.setPos(self.startPositions[item])
            self.updateConnections(item)

    def updateConnections(self, item):
        if hasattr(item, 'connections'):
            for connection in item.connections:
                connection.updatePath()
