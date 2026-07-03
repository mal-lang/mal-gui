import pytest
import xml.etree.ElementTree as ET
from types import SimpleNamespace

from PySide6.QtWidgets import QApplication, QMainWindow, QToolBar, QMessageBox
from PySide6.QtCore import Qt, QPointF

from maltoolbox.language import LanguageGraph
from maltoolbox.model import Model
from malsim import policies
from malsim.config.agent_settings import AttackerSettings, AgentType

from mal_gui.detectors import DetectorIndex
from mal_gui.main_window import MainWindow
from mal_gui.model_scene import ModelScene
from mal_gui.object_explorer import MetaDetectorItem


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
    actions = [
        menu.title() for menu in menu_bar.findChildren(type(menu_bar.addMenu("tmp")))
    ]

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


def test_load_model_recreates_scene(tmp_path, app, lang_file_path):
    window = MainWindow(app, lang_file_path)

    lang_graph = LanguageGraph.load_from_file(lang_file_path)
    model = Model("SavedModel", lang_graph)
    model_path = tmp_path / "saved-model.yml"
    model.save_to_file(str(model_path))

    old_scene = window.scene
    window.load_model(str(model_path))

    assert window.scene is not old_scene
    assert window.scene.model.name == "SavedModel"
    assert window.model_file_name == str(model_path)
    assert window.scenario_file_name is None


def test_load_scenario_uses_current_language_when_lang_file_points_to_scenario(
    tmp_path, app, lang_file_path
):
    import yaml

    window = MainWindow(app, lang_file_path)
    scenario_path = tmp_path / "self-referential-scenario.yml"
    scenario_yaml = {
        "lang_file": str(scenario_path),
        "agents": {},
        "model": {
            "metadata": {
                "name": "SelfReferentialScenario",
                "langVersion": "1.0.0",
                "langID": "org.mal-lang.coreLang",
                "malVersion": "0.1.0-SNAPSHOT",
                "MAL-Toolbox Version": "2.8.1",
                "info": "Test model",
            },
            "assets": {},
        },
    }
    scenario_path.write_text(yaml.safe_dump(scenario_yaml), encoding="utf-8")

    window.load_scenario(str(scenario_path))

    assert window.lang_file_path == lang_file_path
    assert window._lang_file == lang_file_path
    assert window.scene.model.name == "SelfReferentialScenario"
    assert window.scenario_file_name == str(scenario_path)


def test_load_scene_restores_attacker_policy_from_scenario(app, lang_file_path):
    window = MainWindow(app, lang_file_path)

    lang_graph = LanguageGraph.load_from_file(lang_file_path)
    model = Model("ScenarioPolicyModel", lang_graph)
    asset = model.add_asset("Application", name="App1")
    asset.extras = {"position": {"x": 0, "y": 0}}

    scenario = SimpleNamespace(
        agent_settings={
            "Attacker1": AttackerSettings(
                name="Attacker1",
                entry_points={"App1:attemptRead"},
                goals={"App1:successfulRead"},
                type=AgentType.ATTACKER,
                policy=policies.DepthFirstAttacker,
            )
        }
    )

    window.load_scene(lang_file_path, model, scenario)

    assert len(window.scene.attacker_items) == 1
    attacker = window.scene.attacker_items[0]
    assert attacker.policy is policies.DepthFirstAttacker
    assert attacker.entry_points == ["App1:attemptRead"]
    assert attacker.goals == ["App1:successfulRead"]


def test_quick_load_current_file_reloads_model(tmp_path, monkeypatch, app, lang_file_path):
    window = MainWindow(app, lang_file_path)

    lang_graph = LanguageGraph.load_from_file(lang_file_path)
    model = Model("ReloadTarget", lang_graph)
    model_path = tmp_path / "reload-model.yml"
    model.save_to_file(str(model_path))
    window.load_model(str(model_path))

    reloaded_scene = window.scene
    window.scene.model.name = "MutatedInMemory"
    monkeypatch.setattr(QMessageBox, "question", lambda *args, **kwargs: QMessageBox.Ok)

    window.quick_load_current_file()

    assert window.scene is not reloaded_scene
    assert window.scene.model.name == "ReloadTarget"
    assert window.model_file_name == str(model_path)


def test_save_model_persists_attacker_metadata(monkeypatch, main_window):
    asset_item = main_window.scene.create_asset("Application", QPointF(100, 100), name="App1")
    attacker_item = main_window.scene.create_attacker(
        QPointF(25, 50),
        "Attacker1",
        entry_points=["App1:attemptRead"],
        goals=["App1:successfulRead"],
        policy=policies.RandomAgent,
    )

    main_window.model_file_name = "saved-model.yml"
    saved = {}
    monkeypatch.setattr(
        main_window.scene.model,
        "save_to_file",
        lambda path: saved.setdefault("path", path),
    )

    main_window.save_model()

    asset_extras = main_window.scene.model.assets[asset_item.asset.id].extras
    attacker_metadata = asset_extras[main_window.ATTACKER_METADATA_KEY]

    assert saved["path"] == "saved-model.yml"
    assert attacker_metadata == [
        {
            "kind": "attacker",
            "name": "Attacker1",
            "entry_points": ["App1:attemptRead"],
            "goals": ["App1:successfulRead"],
            "policy": "RandomAgent",
            "position": {"x": attacker_item.pos().x(), "y": attacker_item.pos().y()},
        }
    ]


def test_asset_factory_registers_meta_detector(main_window):
    assert "Meta Detector" in main_window.asset_factory.asset_registry


def test_load_model_restores_meta_detector_from_model_metadata(
    tmp_path, app, lang_file_path
):
    import yaml

    window = MainWindow(app, lang_file_path)

    lang_graph = LanguageGraph.load_from_file(lang_file_path)
    model = Model("MetaDetectorRoundTrip", lang_graph)
    asset = model.add_asset("Application", name="App1")
    asset.extras = {"position": {"x": 0, "y": 0}}
    model_path = tmp_path / "meta-detector-model.yml"
    model.save_to_file(str(model_path))

    model_yaml = yaml.safe_load(model_path.read_text())
    model_yaml["model"] = {
        "metadetectors": {
            1: {
                "associated_assets": {asset.id: asset.name},
                "extras": {"position": {"x": 30, "y": 40}},
                "name": "Meta Detector 1",
            }
        }
    }
    model_path.write_text(yaml.safe_dump(model_yaml, sort_keys=False))

    window.load_model(str(model_path))

    assert len(window.scene.attacker_items) == 1
    meta_detector = window.scene.attacker_items[0]
    assert isinstance(meta_detector, MetaDetectorItem)
    assert meta_detector.title == "Meta Detector"
    assert meta_detector.pos() == QPointF(30, 40)
    assert meta_detector.connected_assets == ["App1"]


def test_save_model_preserves_all_loaded_meta_detector_connections(
    tmp_path, app, lang_file_path
):
    import yaml

    window = MainWindow(app, lang_file_path)

    lang_graph = LanguageGraph.load_from_file(lang_file_path)
    model = Model("MetaDetectorConnectionsRoundTrip", lang_graph)
    app1 = model.add_asset("Application", name="App1")
    app1.extras = {"position": {"x": 0, "y": 0}}
    app2 = model.add_asset("Application", name="App2")
    app2.extras = {"position": {"x": 100, "y": 0}}
    model_path = tmp_path / "meta-detector-connections.yml"
    model.save_to_file(str(model_path))

    model_yaml = yaml.safe_load(model_path.read_text())
    model_yaml["model"] = {
        "metadetectors": {
            1: {
                "associated_assets": {
                    app1.id: app1.name,
                    app2.id: app2.name,
                },
                "extras": {"position": {"x": 30, "y": 40}},
                "name": "Meta Detector 1",
            }
        }
    }
    model_path.write_text(yaml.safe_dump(model_yaml, sort_keys=False))

    window.load_model(str(model_path))
    window.save_model()

    saved_yaml = yaml.safe_load(model_path.read_text())
    assert saved_yaml["model"]["metadetectors"] == {
        1: {
            "associated_assets": {
                app1.id: "App1",
                app2.id: "App2",
            },
            "associated_asset_labels": {
                app1.id: 1,
                app2.id: 1,
            },
            "extras": {"position": {"x": 30.0, "y": 40.0}},
            "name": "Meta Detector 1",
        }
    }


def test_save_model_persists_non_default_meta_detector_connection_label(
    tmp_path, main_window
):
    import yaml

    asset_item = main_window.scene.create_asset(
        "Application", QPointF(100, 100), name="App1"
    )
    meta_detector_item = main_window.scene.create_meta_detector(
        QPointF(25, 50),
        "Meta Detector 1",
    )
    meta_detector_item.connected_assets.append("App1")
    meta_detector_item.connected_asset_labels["App1"] = 3

    output_path = tmp_path / "saved-model.yml"
    main_window.model_file_name = str(output_path)

    main_window.save_model()

    saved_yaml = yaml.safe_load(output_path.read_text())
    assert saved_yaml["model"]["metadetectors"][1][
        "associated_asset_labels"
    ] == {asset_item.asset.id: 3}


def test_load_model_restores_meta_detector_connection_label(
    tmp_path, app, lang_file_path
):
    import yaml

    window = MainWindow(app, lang_file_path)

    lang_graph = LanguageGraph.load_from_file(lang_file_path)
    model = Model("MetaDetectorLabelRoundTrip", lang_graph)
    asset = model.add_asset("Application", name="App1")
    asset.extras = {"position": {"x": 0, "y": 0}}
    model_path = tmp_path / "meta-detector-label.yml"
    model.save_to_file(str(model_path))

    model_yaml = yaml.safe_load(model_path.read_text())
    model_yaml["model"] = {
        "metadetectors": {
            1: {
                "associated_assets": {asset.id: asset.name},
                "associated_asset_labels": {asset.id: 4},
                "extras": {"position": {"x": 30, "y": 40}},
                "name": "Meta Detector 1",
            }
        }
    }
    model_path.write_text(yaml.safe_dump(model_yaml, sort_keys=False))

    window.load_model(str(model_path))

    meta_detector = window.scene.attacker_items[0]
    assert meta_detector.connected_asset_labels == {"App1": 4}


def test_save_model_persists_meta_detector_metadata(tmp_path, main_window):
    import yaml

    asset_item = main_window.scene.create_asset(
        "Application", QPointF(100, 100), name="App1"
    )
    meta_detector_item = main_window.scene.create_meta_detector(
        QPointF(25, 50),
        "Meta Detector 1",
    )
    meta_detector_item.connected_assets.append("App1")

    output_path = tmp_path / "saved-model.yml"
    main_window.model_file_name = str(output_path)

    main_window.save_model()

    saved_yaml = yaml.safe_load(output_path.read_text())
    assert saved_yaml["model"]["metadetectors"] == {
        1: {
            "associated_assets": {asset_item.asset.id: "App1"},
            "associated_asset_labels": {asset_item.asset.id: 1},
            "extras": {
                "position": {
                    "x": meta_detector_item.pos().x(),
                    "y": meta_detector_item.pos().y(),
                }
            },
            "name": "Meta Detector 1",
        }
    }


def test_save_current_file_saves_loaded_model_with_meta_detectors(
    tmp_path, main_window
):
    import yaml

    asset_item = main_window.scene.create_asset(
        "Application", QPointF(100, 100), name="App1"
    )
    meta_detector_item = main_window.scene.create_meta_detector(
        QPointF(25, 50),
        "Meta Detector 1",
    )
    meta_detector_item.connected_assets.append("App1")

    output_path = tmp_path / "saved-model.yml"
    main_window.model_file_name = str(output_path)
    main_window.scenario_file_name = None

    main_window.save_current_file()

    saved_yaml = yaml.safe_load(output_path.read_text())
    assert saved_yaml["model"]["metadetectors"] == {
        1: {
            "associated_assets": {asset_item.asset.id: "App1"},
            "associated_asset_labels": {asset_item.asset.id: 1},
            "extras": {
                "position": {
                    "x": meta_detector_item.pos().x(),
                    "y": meta_detector_item.pos().y(),
                }
            },
            "name": "Meta Detector 1",
        }
    }


def test_load_scene_restores_attacker_policy_from_model_metadata(app, lang_file_path):
    window = MainWindow(app, lang_file_path)

    lang_graph = LanguageGraph.load_from_file(lang_file_path)
    model = Model("ModelPolicyRoundTrip", lang_graph)
    asset = model.add_asset("Application", name="App1")
    asset.extras = {
        "position": {"x": 0, "y": 0},
        window.ATTACKER_METADATA_KEY: [
            {
                "name": "Attacker1",
                "entry_points": ["App1:attemptRead"],
                "goals": ["App1:successfulRead"],
                "policy": "BreadthFirstAttacker",
                "position": {"x": 10, "y": 20},
            }
        ],
    }

    window.load_scene(lang_file_path, model)

    assert len(window.scene.attacker_items) == 1
    attacker = window.scene.attacker_items[0]
    assert attacker.policy is policies.BreadthFirstAttacker
    assert attacker.entry_points == ["App1:attemptRead"]
    assert attacker.goals == ["App1:successfulRead"]
    assert attacker.pos() == QPointF(10, 20)


def test_reload_project_from_mal_falls_back_to_empty_project(monkeypatch, main_window):
    messages = []

    main_window.scenario_file_name = "missing-scenario.yml"
    monkeypatch.setattr(QMessageBox, "question", lambda *args, **kwargs: QMessageBox.Ok)
    monkeypatch.setattr(main_window, "show_error_popup", messages.append)

    main_window.reload_project_from_mal()

    assert main_window.scene.model.name == "New Model"
    assert main_window.scenario_file_name is None
    assert main_window.model_file_name is None
    assert messages
    assert "Could not reload scenario file" in messages[0]


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


def test_asset_factory_marks_assets_with_detectors(main_window):
    main_window.detector_index = DetectorIndex(asset_types={"Application"})
    main_window.asset_factory.detector_index = main_window.detector_index

    application_asset = main_window.scene.create_asset(
        "Application", QPointF(80, 80), name="App2"
    )

    assert application_asset.has_detector is True


def test_asset_factory_does_not_mark_assets_without_detectors(main_window):
    main_window.detector_index = DetectorIndex(asset_types={"Application"})
    main_window.asset_factory.detector_index = main_window.detector_index

    credentials_asset = main_window.scene.create_asset(
        "Credentials", QPointF(120, 120), name="Creds1"
    )

    assert credentials_asset.has_detector is False


def test_drawio_export_includes_detector_markers(tmp_path, main_window):
    main_window.detector_index = DetectorIndex(asset_types={"Application"})
    main_window.asset_factory.detector_index = main_window.detector_index
    asset_item = main_window.scene.create_asset(
        "Application", QPointF(80, 80), name="AppWithDetector"
    )

    drawio_path = tmp_path / "detectors.drawio"
    drawio_path.write_text(
        """<?xml version="1.0" ?>
<mxfile>
  <diagram>
    <mxGraphModel>
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        <mxCell id="2" parent="0"/>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
""",
        encoding="utf-8",
    )

    main_window.add_positions_to_model()
    main_window._add_detectors_to_drawio_file(str(drawio_path))

    root = ET.parse(drawio_path).getroot()
    cells_by_id = {
        cell.get("id"): cell for cell in root.findall(".//mxCell") if cell.get("id")
    }
    assert f"detector_{asset_item.asset.id}_stem" in cells_by_id
    assert f"detector_{asset_item.asset.id}_diamond" in cells_by_id
    assert cells_by_id[f"detector_{asset_item.asset.id}_stem"].get("parent") == "1"
    assert cells_by_id[f"detector_{asset_item.asset.id}_diamond"].get("parent") == "1"


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
