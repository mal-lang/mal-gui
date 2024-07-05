from PySide6.QtGui import QUndoCommand, QUndoStack

class DeleteCommand(QUndoCommand):
    def __init__(self, scene, item, parent=None):
        super().__init__(parent)
        self.scene = scene
        self.item = item
        # self.connections = []
        self.connections = self.item.connections.copy()
        self.scene.model.remove_asset(item.asset)

    def redo(self):
        # Store the connections before removing the item
        if hasattr(self.item, 'connections'):
            for connection in self.connections:
                connection.delete()

        #At the end remove the item
        self.scene.removeItem(self.item)

    def undo(self):
        self.scene.addItem(self.item)

        # Restore the connections
        for connection in self.connections:
            self.scene.addItem(connection)
            connection.restoreLabels()
            connection.updatePath()
