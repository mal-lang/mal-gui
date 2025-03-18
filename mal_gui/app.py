"""Entry scripts for the MAL GUI"""

import configparser
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
from .main_window import MainWindow

class FileSelectionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Load MAL Language")
        self.setFixedWidth(400)

        # Dialog layout
        vertical_layout = QVBoxLayout()

        # Label to instruct the user
        self.label = QLabel("Select MAL Language .mal/.mar file to load:")
        vertical_layout.addWidget(self.label)

        horizontal_layout = QHBoxLayout()
        self.lang_file_path_text = QLineEdit(self)

        # Load the config file containing latest lang file path
        config_file_dir = user_config_dir("mal-gui", "mal-lang")
        self.config_file_path = config_file_dir + '/config.ini'

        # Make sure config file exists
        os.makedirs(os.path.dirname(self.config_file_path), exist_ok=True)

        self.config = configparser.ConfigParser()
        self.config.read(self.config_file_path)
        self.selected_lang_file = self.config.get(
            'Settings', 'langFilePath', fallback=None)
        print(f"Initial langFilePath path: {self.selected_lang_file}")

        self.lang_file_path_text.setText(self.selected_lang_file)
        horizontal_layout.addWidget(self.lang_file_path_text)

        browse_button = QPushButton("Browse")
        horizontal_layout.addWidget(browse_button)

        vertical_layout.addLayout(horizontal_layout)

        # Create custom buttons for "Load" and "Quit"
        self.button_box = QDialogButtonBox()
        load_button = QPushButton("Load")
        quit_button = QPushButton("Quit")
        self.button_box.addButton(load_button, QDialogButtonBox.AcceptRole)
        self.button_box.addButton(quit_button, QDialogButtonBox.RejectRole)
        vertical_layout.addWidget(self.button_box)

        self.setLayout(vertical_layout)

        browse_button.clicked.connect(self.open_file_dialog)
        load_button.clicked.connect(self.save_lang_file_path)
        quit_button.clicked.connect(self.reject)

    def open_file_dialog(self):
        """Ask user for MAL or MAR file in dialog"""
        file_dialog = QFileDialog()

        file_dialog.setNameFilter("MAL or MAR files (*.mal *.mar)")
        file_dialog.setWindowTitle("Select a MAL or MAR File")

        if file_dialog.exec() == QFileDialog.Accepted:
            selected_lang_path = file_dialog.selectedFiles()[0]
            self.lang_file_path_text.setText(selected_lang_path)

    def save_lang_file_path(self):
        """
        Set current language MAL or MAR file and store latest chosen language
        in user config file
        """

        selected_lang_file = self.lang_file_path_text.text()

        if selected_lang_file.endswith('.mar') or \
                selected_lang_file.endswith('.mal'):
            self.selected_lang_file = selected_lang_file

            # Remember language choice in user settings
            try:
                self.config.add_section('Settings')
            except configparser.DuplicateSectionError:
                pass

            self.config.set('Settings', 'langFilePath',
                self.selected_lang_file)

            with open(self.config_file_path, 'w', encoding='utf-8') as conf_file:
                self.config.write(conf_file)

            self.accept()  # Close the dialog and return accepted
        else:
            QMessageBox.warning(
                self, "Invalid File",
                "Please select a valid .mal or .mar file.")

    def get_selected_file(self):
        return self.selected_lang_file


def main():
    """Entrypoint of MAL GUI"""
    app = QApplication(sys.argv)

    dialog = FileSelectionDialog()
    if dialog.exec() == QDialog.Accepted:
        selected_lang_path = dialog.get_selected_file()
        window = MainWindow(app, selected_lang_path)
        window.show()
        print(f"Selected MAL/MAR file Path: {selected_lang_path}")
        app.exec()
    else:
        app.quit()


if __name__ == "__main__":
    main()
