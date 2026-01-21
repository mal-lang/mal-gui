import pytest

from PySide6.QtWidgets import QApplication, QMainWindow, QToolBar
from PySide6.QtCore import Qt, QPointF

from maltoolbox.language import LanguageGraph
from maltoolbox.model import Model

from mal_gui.main_window import MainWindow
from mal_gui.model_scene import ModelScene


@pytest.fixture
def main_window(app, lang_file_path):
    """Create a MainWindow instance."""
    window = MainWindow(app, lang_file_path)
    yield window
    window.close()


# -------------------------------------------------------------------
# Initialization
# -------------------------------------------------------------------

def test_main_window_initialization(main_window):
    assert isinstance(main_window, QMainWindow)
    assert main_window.windowTitle() == "MAL GUI"

    # Core attributes
    assert main_window.scene is not None
    assert main_window.view is not None
    assert main_window.asset_factory is not None

    # Toolbar exists
    assert isinstance(main_window.toolbar, QToolBar)

    # Dock widgets created
    assert len(main_window.dock_widgets) > 0


def test_scene_is_model_scene(main_window):
    assert isinstance(main_window.scene, ModelScene)
    assert isinstance(main_window.scene.model, Model)


# -------------------------------------------------------------------
# Menu & Actions
# -------------------------------------------------------------------

def test_menu_bar_created(main_window):
    menu_bar = main_window.menuBar()
    actions = [menu.title() for menu in menu_bar.findChildren(type(menu_bar.addMenu("tmp")))]

    assert "&File" in actions
    assert "Edit" in actions


def test_actions_exist(main_window):
    assert main_window.zoom_in_action is not None
    assert main_window.zoom_out_action is not None
    assert main_window.undo_action is not None
    assert main_window.redo_action is not None
    assert main_window.cut_action is not None
    assert main_window.copy_action is not None
    assert main_window.paste_action is not None
    assert main_window.delete_action is not None


# -------------------------------------------------------------------
# Toolbar behavior
# -------------------------------------------------------------------

def test_zoom_actions(main_window):
    initial_zoom = main_window.view.zoom_factor

    main_window.zoom_in()
    assert main_window.view.zoom_factor > initial_zoom

    main_window.zoom_out()
    assert main_window.view.zoom_factor <= initial_zoom


def test_zoom_line_edit(main_window):
    main_window.zoom_line_edit.setText("150")
    main_window.set_zoom_level_from_line_edit()

    assert int(main_window.view.zoom_factor * 100) == 150
    assert main_window.zoom_label.text() == "150%"


# -------------------------------------------------------------------
# Scene reload / clearing
# -------------------------------------------------------------------

def test_clear_window(main_window):
    # Sanity: items exist initially
    assert main_window.scene is not None
    assert main_window.toolbar is not None

    main_window.clear_window()

    # Menu bar cleared
    assert main_window.menuBar().actions() == []


def test_load_scene_recreates_components(app, lang_file_path):
    window = MainWindow(app, lang_file_path)

    old_scene = window.scene
    lang_graph = LanguageGraph.load_from_file(lang_file_path)
    model = Model("ReloadedModel", lang_graph)

    window.load_scene(lang_file_path, model)

    assert window.scene is not old_scene
    assert window.scene.model.name == "ReloadedModel"


# -------------------------------------------------------------------
# Object explorer update signal
# -------------------------------------------------------------------

def test_update_explorer_signal(main_window):
    # Should not raise
    main_window.update_childs_in_object_explorer_signal.emit()


# -------------------------------------------------------------------
# Theme handling
# -------------------------------------------------------------------

def test_theme_selection(main_window):
    # First item is "None"
    main_window.theme_combo_box.setCurrentIndex(0)
    assert main_window.theme_combo_box.currentText() == "None"


# -------------------------------------------------------------------
# Model interaction (lightweight)
# -------------------------------------------------------------------

def test_add_asset_updates_scene(main_window):
    scene = main_window.scene

    pos = QPointF(100, 100)
    asset = scene.create_asset("Application", pos, name="App1")

    assert asset in scene.items()


# -------------------------------------------------------------------
# Quit behavior
# -------------------------------------------------------------------

def test_quit_app_calls_app_quit(monkeypatch, main_window):
    called = {"quit": False}

    def fake_quit():
        called["quit"] = True

    monkeypatch.setattr(main_window.app, "quit", fake_quit)
    main_window.quitApp()

    assert called["quit"] is True
