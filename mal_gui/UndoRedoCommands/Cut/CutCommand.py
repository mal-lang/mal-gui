from PySide6.QtGui import QUndoCommand, QUndoStack

class CutCommand(QUndoCommand):
    def __init__(self, scene, item, clipboard, parent=None):
        super().__init__(parent)
        self.scene = scene
        self.item = item
        self.clipboard = clipboard
        self.connections = self.item.connections.copy()

    def redo(self):
        self.cutItemFlag = True
        serializedData = self.scene.serializeGraphicsItem(self.item, self.cutItemFlag)
        self.clipboard.clear()
        self.clipboard.setText(serializedData) 
        
        # Remove connections if any, before removing the item
        if hasattr(self.item, 'connections'):
            for connection in self.connections:
                connection.delete()

        self.scene.removeItem(self.item)

    def undo(self):
        self.scene.addItem(self.item)
        
        # Restore the connections and their labels
        for connection in self.connections:
            self.scene.addItem(connection)
            connection.restoreLabels()
            connection.updatePath()
        
        self.clipboard.clear()