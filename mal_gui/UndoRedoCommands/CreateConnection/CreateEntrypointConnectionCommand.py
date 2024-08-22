from PySide6.QtGui import QUndoCommand
from ConnectionItem import EntrypointConnectionItem

class CreateEntrypointConnectionCommand(QUndoCommand):
    def __init__(
        self,
        scene,
        startItem,
        endItem,
        entrypointText,
        selectedItemEntrypoint,
        parent=None
    ):
        super().__init__(parent)
        self.scene = scene
        self.startItem = startItem
        self.endItem = endItem
        self.entrypointText = entrypointText
        self.connection = None
        self.entrypoint = selectedItemEntrypoint
        

    def redo(self):
        self.connection = self.scene.addEntryPointConnection(
            self.entrypointText,
            self.startItem,
            self.endItem
        )

        # self.scene.model.add_entrypoint(self.entrypoint) - Need to check with Andrei for mal-tool box methods

    def undo(self):
        self.connection.removeLabels()
        self.scene.removeItem(self.connection)
        # self.scene.model.remove_entrypoint(self.entrypoint) - Need to check with Andrei for mal-tool box methods
