import pytest
from PySide6.QtWidgets import QApplication

@pytest.fixture
def lang_file_path():
    return "tests/testdata/org.mal-lang.coreLang-1.0.0.mar"


@pytest.fixture(scope="session")
def app():
    """
    Single QApplication instance for the entire test session.
    Qt allows only one QApplication per process.
    """
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app
