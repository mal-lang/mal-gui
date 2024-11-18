from PySide6.QtGui import QUndoCommand
class DragDropCommand(QUndoCommand):
    def __init__(self, scene, item, parent=None):
        super().__init__(parent)
        self.scene = scene
        self.item = item

    def redo(self):
        self.scene.addItem(self.item)

        #Update the Object Explorer when number of items change
        self.scene.mainWindow.updateChildsInObjectExplorerSignal.emit()

    def undo(self):
        self.scene.removeItem(self.item)

        #Update the Object Explorer when number of items change
        self.scene.mainWindow.updateChildsInObjectExplorerSignal.emit()
