from PySide6.QtWidgets import QApplication,QDialog,QVBoxLayout,QHBoxLayout,QLabel,QLineEdit,QPushButton,QDialogButtonBox,QFileDialog,QMessageBox
from MainWindow import MainWindow
import sys 

import configparser

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
        self.marFilePath = self.config.get('Settings', 'marFilePath')
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
            
            self.config.set('Settings', 'marFilePath', self.selectedFile)
            with open('config.ini', 'w') as configfile:
                self.config.write(configfile)
            
            
            self.accept()  # Close the dialog and return accepted
        else:
            QMessageBox.warning(self, "Invalid File", "Please select a valid .mar file.")
    
    def getSelectedFile(self):
        return self.selectedFile



if __name__ == "__main__":
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
    