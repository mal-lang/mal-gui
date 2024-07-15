from PySide6.QtWidgets import QApplication
from MainWindow import MainWindow
import sys 

app = QApplication(sys.argv)

window = MainWindow(app)
window.show()

app.exec()