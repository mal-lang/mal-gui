from PySide6.QtGui import QUndoCommand

class DeleteCommand(QUndoCommand):
    def __init__(self, scene, items, parent=None):
        super().__init__(parent)
        self.scene = scene
        self.items = items
        self.connections = []

        # Save connections of all items
        for item in self.items:
            if hasattr(item, 'connections'):
                self.connections.extend(item.connections.copy())

    def redo(self):
        # Store the connections before removing the items
        for connection in self.connections:
            connection.removeLabels()
            self.scene.removeItem(connection)
        
        for item in self.items:
            self.scene.removeItem(item)
            self.scene.model.remove_asset(item.asset)
            
        #Update the Object Explorer when number of items change
        self.scene.mainWindow.updateChildsInObjectExplorerSignal.emit()

    def undo(self):
        # Add items back to the scene
        for item in self.items:
            self.scene.addItem(item)
        
        # Restore connections
        for connection in self.connections:
            self.scene.addItem(connection)
            connection.restoreLabels()
            connection.updatePath()
            
        #Update the Object Explorer when number of items change
        self.scene.mainWindow.updateChildsInObjectExplorerSignal.emit()