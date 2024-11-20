from PySide6.QtWidgets import QListWidget

class AttackStepsWindow(QListWidget):
    def __init__(self, parent=None):
        super(AttackStepsWindow, self).__init__(parent)
