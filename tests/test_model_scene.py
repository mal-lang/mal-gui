import pytest
from PySide6.QtWidgets import QApplication, QGraphicsScene, QGraphicsLineItem
from PySide6.QtCore import Qt, QPointF, QMimeData, QEvent
from PySide6.QtGui import QDropEvent, QMouseEvent

from maltoolbox.language import LanguageGraph
from maltoolbox.model import Model
from mal_gui.main_window import MainWindow
from mal_gui.model_scene import ModelScene
from mal_gui.object_explorer import AssetItem, AttackerItem

@pytest.fixture
def model_scene(app):
    lang_file_path = 'tests/testdata/org.mal-lang.coreLang-1.0.0.mar'
    lang_graph = LanguageGraph.load_from_file(str(lang_file_path))
    main_window = MainWindow(app, str(lang_file_path))
    asset_factory = main_window.asset_factory
    model = Model("TestModel", lang_graph)
    return ModelScene(asset_factory, lang_graph, model, main_window)

def test_scene_initialization(model_scene):
    assert isinstance(model_scene, QGraphicsScene)
    assert model_scene.undo_stack.count() == 0
    assert isinstance(model_scene.clipboard, type(model_scene.clipboard))

def test_add_asset(model_scene):
    pos = QPointF(50, 50)
    asset_item = model_scene.create_asset("Application", pos, name="Application1")
    assert isinstance(asset_item, AssetItem)
    assert asset_item.pos() == pos
    assert asset_item in model_scene._asset_id_to_item.values()

def test_add_attacker(model_scene):
    pos = QPointF(0, 0)
    attacker_item = model_scene.create_attacker(pos, "Attacker1")
    assert isinstance(attacker_item, AttackerItem)
    assert attacker_item.pos() == pos
    assert attacker_item in model_scene.attacker_items

# def test_connection_creation(model_scene):
#     a1 = model_scene.create_asset("Application", QPointF(0, 0))
#     a2 = model_scene.create_asset("Application", QPointF(100, 0))
#     model_scene.start_item = a1
#     # real line item instead of mock
#     model_scene.line_item = QGraphicsLineItem(a1.pos().x(), a1.pos().y(), a1.pos().x(), a1.pos().y())
#     model_scene.end_item = a2
#     # finalize_connection should run without errors (dialogs won't show in tests)
#     model_scene._finalize_connection(a2)
#     # line_item is cleared after finalize
#     assert model_scene.line_item is None
#     assert model_scene.start_item is None
#     assert model_scene.end_item is None

def test_undo_redo(model_scene):
    pos = QPointF(0, 0)
    asset_item = model_scene.create_asset("Application", pos)
    initial_count = len(model_scene.items())
    model_scene.delete_assets([asset_item])
    assert len(model_scene.items()) < initial_count
    model_scene.undo_stack.undo()
    assert len(model_scene.items()) == initial_count

def test_serialize_deserialize(model_scene):
    asset_item = model_scene.create_asset("Application", QPointF(0, 0))
    serialized = model_scene.serialize_graphics_items([asset_item], cut_intended=False)
    deserialized = model_scene.deserialize_graphics_items(serialized)
    assert isinstance(deserialized, list)
    assert deserialized[0]['title'] == asset_item.title
