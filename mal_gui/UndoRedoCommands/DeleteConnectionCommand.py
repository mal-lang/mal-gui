from PySide6.QtGui import QUndoCommand

class DeleteConnectionCommand(QUndoCommand):
    def __init__(self, scene, item, parent=None):
        super().__init__(parent)
        self.scene = scene
        self.connection = item

    def redo(self):
        # self.connection.delete()
        self.connection.removeLabels()
        self.scene.removeItem(self.connection)

    def undo(self):
        self.scene.addItem(self.connection)
        self.connection.restoreLabels()
        self.connection.updatePath()
