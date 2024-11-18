import sys

if __name__ == "__main__" and __package__ is None:
    print(
        "Warning: You are running 'app.py' directly.\n"
        "Please install the package and use the 'malgui' command instead\n"
        "or use 'python3 -m mal_gui.app' from the parent directory."
    )
    sys.exit(1)  # Exit to prevent accidental misuse

import configparser

from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QDialogButtonBox,
    QFileDialog,
    QMessageBox
)
from .MainWindow import MainWindow

class FileSelectionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Load MAL Language")
        self.setFixedWidth(400)

        # Dialog layout
        verticalLayout = QVBoxLayout()

        # Label to instruct the user
        self.label = QLabel("Select MAL Language mar file to load:")
        verticalLayout.addWidget(self.label)

        horizontalLayout = QHBoxLayout()

        self.malLanguageMarFilePathText = QLineEdit(self)
        
        # Load the config file
        self.config = configparser.ConfigParser()
        # self.config.read('config.ini')
        self.config.read('config.ini')
        self.marFilePath = self.config.get('Settings', 'marFilePath', fallback=None)
        print(f"Initial marFilePath path: {self.marFilePath}")
        self.malLanguageMarFilePathText.setText(self.marFilePath)
        
        horizontalLayout.addWidget(self.malLanguageMarFilePathText)

        browseButton = QPushButton("Browse")
        horizontalLayout.addWidget(browseButton)

        verticalLayout.addLayout(horizontalLayout)

        # Create custom buttons for "Load" and "Quit"
        self.buttonBox = QDialogButtonBox()
        loadButton = QPushButton("Load")
        quitButton = QPushButton("Quit")
        self.buttonBox.addButton(loadButton, QDialogButtonBox.AcceptRole)
        self.buttonBox.addButton(quitButton, QDialogButtonBox.RejectRole)
        verticalLayout.addWidget(self.buttonBox)

        self.setLayout(verticalLayout)

        browseButton.clicked.connect(self.openFileDialog)
        loadButton.clicked.connect(self.loadFile)
        quitButton.clicked.connect(self.reject)

    def openFileDialog(self):
        fileDialog = QFileDialog()
        
        # fileDialog.setNameFilter("JAR or MAR files (*.jar *.mar )") --> Need to confirm with Andrei
        # fileDialog.setWindowTitle("Select a JAR or MAR File") 
        
        fileDialog.setNameFilter("MAR files (*.mar)")
        fileDialog.setWindowTitle("Select a MAR File")

        if fileDialog.exec() == QFileDialog.Accepted:
            selectedFilePath = fileDialog.selectedFiles()[0]
            self.malLanguageMarFilePathText.setText(selectedFilePath)

    def loadFile(self):
        selectedFile = self.malLanguageMarFilePathText.text()

        # Check if the path ends with .mar or .jar --> Need to confirm with Andrei
        # if selectedFile.endswith(('.jar','.mar')):
        
        if selectedFile.endswith('.mar'):
            self.selectedFile = selectedFile
            self.accept()  # Close the dialog and return accepted
        else:
            QMessageBox.warning(self, "Invalid File", "Please select a valid .mar file.")
    
    def getSelectedFile(self):
        return self.selectedFile


def main():
    app = QApplication(sys.argv)

    dialog = FileSelectionDialog()
    if dialog.exec() == QDialog.Accepted:
        selectedFilePath = dialog.getSelectedFile()

        window = MainWindow(app,selectedFilePath)
        window.show()

        print(f"Selected MAR file Path: {selectedFilePath}")

        app.exec()
    else:
        app.quit()


if __name__ == "__main__":
    main()
