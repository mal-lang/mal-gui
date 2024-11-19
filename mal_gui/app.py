import os
import sys

from appdirs import user_config_dir

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
        self.label = QLabel("Select MAL Language .mar file to load:")
        verticalLayout.addWidget(self.label)

        horizontalLayout = QHBoxLayout()
        self.malLangFilePathText = QLineEdit(self)

        # Load the config file containing latest lang file path
        config_file_dir = user_config_dir("mal-gui", "mal-lang")
        self.config_file_path = config_file_dir + '/config.ini'

        # Make sure config file exists
        os.makedirs(os.path.dirname(self.config_file_path), exist_ok=True)

        self.config = configparser.ConfigParser()
        self.config.read(self.config_file_path)
        self.selectedLangFile = self.config.get(
            'Settings', 'langFilePath', fallback=None)
        print(f"Initial langFilePath path: {self.selectedLangFile}")
        self.malLangFilePathText.setText(self.selectedLangFile)

        horizontalLayout.addWidget(self.malLangFilePathText)

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
        loadButton.clicked.connect(self.saveLangFilePath)
        quitButton.clicked.connect(self.reject)

    def openFileDialog(self):
        fileDialog = QFileDialog()

        # fileDialog.setNameFilter("JAR or MAR files (*.jar *.mar )") --> Need to confirm with Andrei
        # fileDialog.setWindowTitle("Select a JAR or MAR File")

        fileDialog.setNameFilter("MAR files (*.mar)")
        fileDialog.setWindowTitle("Select a MAR File")

        if fileDialog.exec() == QFileDialog.Accepted:
            selectedLangFilePath = fileDialog.selectedFiles()[0]
            self.malLangFilePathText.setText(selectedLangFilePath)

    def saveLangFilePath(self):
        """
        Set current language MAR archive file and store
        latest chosen language in user config file
        """

        selectedLangFile = self.malLangFilePathText.text()

        if selectedLangFile.endswith('.mar'):
            self.selectedLangFile = selectedLangFile

            # Remember language choice in user settings
            self.config.set('Settings', 'langFilePath', self.selectedLangFile)
            with open(self.config_file_path, 'w') as configfile:
                self.config.write(configfile)

            self.accept()  # Close the dialog and return accepted
        else:
            QMessageBox.warning(self, "Invalid File", "Please select a valid .mar file.")

    def getSelectedFile(self):
        return self.selectedLangFile


def main():
    app = QApplication(sys.argv)

    dialog = FileSelectionDialog()
    if dialog.exec() == QDialog.Accepted:
        selectedLangFilePath = dialog.getSelectedFile()
        window = MainWindow(app, selectedLangFilePath)
        window.show()
        print(f"Selected MAR file Path: {selectedLangFilePath}")

        app.exec()
    else:
        app.quit()


if __name__ == "__main__":
    main()
