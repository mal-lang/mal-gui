import sys
from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT_STR = str(PROJECT_ROOT)
if PROJECT_ROOT_STR in sys.path:
    sys.path.remove(PROJECT_ROOT_STR)
sys.path.insert(0, PROJECT_ROOT_STR)


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
