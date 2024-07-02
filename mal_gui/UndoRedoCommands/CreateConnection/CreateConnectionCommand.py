from PySide6.QtGui import QUndoCommand
from ConnectionItem import ConnectionItem

class CreateConnectionCommand(QUndoCommand):
    def __init__(self, scene, startItem, endItem, associationText, parent=None):
        super().__init__(parent)
        self.scene = scene
        self.startItem = startItem
        self.endItem = endItem
        self.associationText = associationText
        self.connection = None

    def redo(self):
        if self.connection is None:
            self.connection = ConnectionItem(self.associationText, self.startItem, self.endItem, self.scene)
        self.scene.addItem(self.connection)
        self.connection.restoreLabels()
        self.connection.updatePath()

    def undo(self):
        self.connection.removeLabels()
        self.scene.removeItem(self.connection)
