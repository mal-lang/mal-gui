import inspect
from os import fspath
from pathlib import Path
from typing import Optional
import xml.etree.ElementTree as ET
from xml.dom import minidom

from PySide6.QtWidgets import (
    QWidget,
    QLineEdit,
    QSplitter,
    QMainWindow,
    QToolBar,
    QDockWidget,
    QListWidget,
    QComboBox,
    QLabel,
    QTreeWidget,
    QCheckBox,
    QPushButton,
    QFileDialog,
    QMessageBox,
    QTableWidgetItem,
    QApplication,
)
from PySide6.QtGui import QDrag, QAction, QIcon, QIntValidator
from PySide6.QtCore import Qt, QMimeData, QByteArray, QSize, Signal, QPointF

from malsim import DefenderSettings
from qt_material import apply_stylesheet, list_themes

from maltoolbox import __version__ as maltoolbox_version
from maltoolbox.language import LanguageGraph
from maltoolbox.model import Model, ModelAsset
from maltoolbox.exceptions import ModelException
from malsim.config.agent_settings import AttackerSettings, AgentType
from malsim.scenario import Scenario
import yaml

from mal_gui.object_explorer.attacker_item import AttackerItem

from .file_utils import image_path
from .model_scene import ModelScene
from .model_view import ModelView
from .object_explorer import AssetItem, AssetFactory
from .detectors import load_detector_index
from .assets_container.assets_container import AssetsContainer
from .connection_item import AssociationConnectionItem
from .docked_windows import (
    DraggableTreeView,
    ItemDetailsWindow,
    PropertiesWindow,
    EditableDelegate,
    AttackStepsWindow,
    AssetRelationsWindow,
)

# Used to create absolute paths of assets
PACKAGE_DIR = Path(__file__).resolve().parent


def _path_to_str(file_path) -> str:
    return fspath(file_path)


class DraggableListWidget(QListWidget):
    def mousePressEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            item = self.itemAt(event.position().toPoint())
            if item:
                drag = QDrag(self)
                mime_data = QMimeData()
                mime_data.setData(
                    "application/x-qabstractitemmodeldatalist", QByteArray()
                )
                mime_data.setData("text/plain", item.text().encode())
                drag.setMimeData(mime_data)
                drag.exec()


class MainWindow(QMainWindow):
    ATTACKER_METADATA_KEY = "_mal_gui_attackers"
    META_DETECTORS_MODEL_KEY = "metadetectors"
    update_childs_in_object_explorer_signal = Signal()

    def __init__(self, app: QApplication, lang_file_path: str):
        super().__init__()
        self.setWindowTitle("MAL GUI")
        self.app = app  # declare an app member

        self.scenario_file_name = None
        self.model_file_name = None

        self.lang_file_path = _path_to_str(lang_file_path)
        self._loaded_meta_detector_data: list[dict] = []
        lang_graph = LanguageGraph.load_from_file(self.lang_file_path)
        self.detector_index = load_detector_index(self.lang_file_path)
        self.asset_factory = self.create_asset_factory(lang_graph)
        self.scene = self.create_scene(
            lang_graph,
            self.asset_factory,
            Model("New Model", lang_graph),
            meta_detector_metadata=self._loaded_meta_detector_data,
        )

        self.create_actions(self.scene)
        self.create_menu_bar()
        self.toolbar = self.create_toolbar()
        self.addToolBar(self.toolbar)
        self.dock_widgets = self.create_side_panels(self.asset_factory)

        self.view = self.create_view(self.scene)

    def clear_window(self):
        """Clear everything from the window"""
        print("CLEAR WINDOW")

        # Clear the scene (where the model is shown)
        self.scene.clear()
        # Remove the toolbar with actions and icons (above scene)
        self.removeToolBar(self.toolbar)
        # Remove top dropdown menu bar ('File', 'Edit')
        self.menuBar().clear()

        # Remove the dock widgets (left menu)
        for dock_widget in self.dock_widgets:
            self.removeDockWidget(dock_widget)

    def load_scene(
        self, lang_file_path: str, model: Model, scenario: Optional[Scenario] = None
    ):
        """Load scene with given language and model"""
        print("LOADING SCENE!")
        lang_file_path = _path_to_str(lang_file_path)
        lang_graph = LanguageGraph.load_from_file(lang_file_path)
        self.clear_window()
        self.lang_file_path = lang_file_path
        self.detector_index = load_detector_index(lang_file_path)
        self.asset_factory = self.create_asset_factory(lang_graph)
        self.scene = self.create_scene(
            lang_graph,
            self.asset_factory,
            model,
            scenario,
            meta_detector_metadata=self._loaded_meta_detector_data,
        )

        self.create_actions(self.scene)
        self.create_menu_bar()
        self.toolbar = self.create_toolbar()
        self.addToolBar(self.toolbar)
        self.dock_widgets = self.create_side_panels(self.asset_factory)
        self.view = self.create_view(self.scene)

    def create_asset_factory(self, lang_graph: LanguageGraph):
        """Create asset factory for language"""
        asset_images = {
            "Application": image_path("application.png"),
            "Credentials": image_path("credentials.png"),
            "Data": image_path("datastore.png"),
            "Group": image_path("group.png"),
            "Hardware": image_path("hardware.png"),
            "HardwareVulnerability": image_path("hardwareVulnerability.png"),
            "IDPS": image_path("idps.png"),
            "Identity": image_path("identity.png"),
            "Privileges": image_path("privileges.png"),
            "Information": image_path("information.png"),
            "Network": image_path("network.png"),
            "ConnectionRule": image_path("connectionRule.png"),
            "PhysicalZone": image_path("physicalZone.png"),
            "RoutingFirewall": image_path("routingFirewall.png"),
            "SoftwareProduct": image_path("softwareProduct.png"),
            "SoftwareVulnerability": image_path("softwareVulnerability.png"),
            "User": image_path("user.png"),
        }

        # Create a registry as a dictionary containing
        # name as key and class as value
        asset_factory = AssetFactory(detector_index=self.detector_index)
        asset_factory.register_asset("Attacker", image_path("attacker.png"))
        asset_factory.register_asset("Meta Detector", image_path("metadetector.png"))

        for asset in lang_graph.assets.values():
            if not asset.is_abstract:
                asset_factory.register_asset(
                    asset.name, asset_images.get(asset.name, image_path("unknown.png"))
                )

        return asset_factory

    def create_scene(
        self,
        lang_graph: LanguageGraph,
        asset_factory: AssetFactory,
        model: Model,
        scenario: Optional[Scenario] = None,
        meta_detector_metadata: Optional[list[dict]] = None,
    ):
        """Create and initialize scene from language"""

        model_scene = ModelScene(
            asset_factory,
            lang_graph,
            model,
            self,
            scenario,
            meta_detector_metadata=meta_detector_metadata,
        )

        return model_scene

    def create_view(self, scene: ModelScene):
        """Create and initialize view"""
        view = ModelView(scene, self)
        view.zoom_changed.connect(self.update_zoom_label)
        splitter = QSplitter()
        splitter.addWidget(view)

        # Set initial sizes of widgets in splitter
        splitter.setSizes([200, 100])
        self.setCentralWidget(splitter)
        self.update_childs_in_object_explorer_signal.connect(
            self.update_explorer_docked_window
        )
        return view

    def create_side_panels(self, asset_factory: AssetFactory):
        """Add side panel objects"""

        dock_widgets = []

        # ObjectExplorer - LeftSide pannel is Draggable TreeView
        dock_object_explorer = QDockWidget("Object Explorer", self)
        eye_unhide_icon_image = image_path("eyeUnhide.png")
        eye_hide_icon_image = image_path("eyeHide.png")
        rgb_color_icon_image = image_path("rgbColor.png")

        self.object_explorer_tree = DraggableTreeView(
            self.scene, eye_unhide_icon_image, eye_hide_icon_image, rgb_color_icon_image
        )

        for _, values in asset_factory.asset_registry.items():
            for value in values:
                self.object_explorer_tree.set_parent_item_text(
                    value.asset_type, value.asset_image
                )

        dock_object_explorer.setWidget(self.object_explorer_tree)
        self.addDockWidget(Qt.LeftDockWidgetArea, dock_object_explorer)
        dock_widgets.append(dock_object_explorer)

        # EDOC Tab with treeview
        component_tab_tree = QTreeWidget()
        component_tab_tree.setHeaderLabel(None)

        # ItemDetails with treeview
        self.item_details_window = ItemDetailsWindow()
        dock_item_details = QDockWidget("Item Details", self)
        dock_item_details.setWidget(self.item_details_window)
        self.addDockWidget(Qt.LeftDockWidgetArea, dock_item_details)
        dock_widgets.append(dock_item_details)

        # Properties Tab with tableview
        self.properties_docked_window = PropertiesWindow()
        self.properties_table = self.properties_docked_window.properties_table
        dock_properties = QDockWidget("Properties", self)
        dock_properties.setWidget(self.properties_table)
        self.addDockWidget(Qt.LeftDockWidgetArea, dock_properties)
        dock_widgets.append(dock_properties)

        # AttackSteps Tab with ListView
        self.attack_steps_docked_window = AttackStepsWindow()
        dock_attack_steps = QDockWidget("Attack Steps", self)
        dock_attack_steps.setWidget(self.attack_steps_docked_window)
        self.addDockWidget(Qt.LeftDockWidgetArea, dock_attack_steps)
        dock_widgets.append(dock_attack_steps)

        # AssetRelations Tab with ListView
        self.asset_relations_docker_window = AssetRelationsWindow()
        dock_asset_relations = QDockWidget("Asset Relations", self)
        dock_asset_relations.setFeatures(
            QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetMovable
        )
        dock_asset_relations.setWidget(self.asset_relations_docker_window)
        self.addDockWidget(Qt.LeftDockWidgetArea, dock_asset_relations)
        dock_widgets.append(dock_asset_relations)

        # Keep Propeties Window and Attack Step Window Tabbed
        self.tabifyDockWidget(dock_properties, dock_attack_steps)

        # Keep the properties Window highlighted and raised
        dock_properties.raise_()

        return dock_widgets

    def show_association_checkbox_changed(self, checked):
        """Called on button click"""
        print("self.show_association_checkbox_changed clicked")
        self.scene.set_show_assoc_checkbox_status(checked)
        for connection in self.scene.items():
            if isinstance(connection, AssociationConnectionItem):
                connection.update_path()

    def show_image_icon_checkbox_changed(self, checked):
        """Called on button click"""
        print("self.show_image_icon_checkbox_changed clicked")
        for item in self.scene.items():
            if isinstance(item, (AssetItem, AssetsContainer)):
                item.toggle_icon_visibility()

    def fit_to_view_button_clicked(self):
        """Called on button click"""
        print("Fit To View Button Clicked..")
        # Find the bounding rectangle of all items in Scene
        bounding_rect = self.scene.itemsBoundingRect()
        self.view.fitInView(bounding_rect, Qt.KeepAspectRatio)

    def update_properties_window(self, asset_item: AssetItem):
        # Clear the table
        self.properties_table.setRowCount(0)

        if asset_item is not None:
            asset = asset_item.asset
            properties = []
            for attack_step_name, value in asset.defenses.items():
                # Add defenses that are set in model
                attack_step = asset.lg_asset.attack_steps[attack_step_name]
                if attack_step.ttc and len(attack_step.ttc["arguments"]) > 0:
                    default_value = attack_step.ttc["arguments"][0]
                else:
                    default_value = 0.0
                properties.append((attack_step_name, str(value), str(default_value)))

            for attack_step in asset.lg_asset.attack_steps.values():
                # Add defenses that are not set in model
                if attack_step.name in asset.defenses:
                    continue
                if attack_step.type == "defense":
                    if attack_step.ttc and len(attack_step.ttc["arguments"]) > 0:
                        default_value = attack_step.ttc["arguments"][0]
                    else:
                        default_value = 0.0
                    properties.append((attack_step.name, "", str(default_value)))

            # Insert new rows based on the data dictionary
            num_rows = len(properties)
            self.properties_table.setRowCount(num_rows)
            self.properties_table.currentItem = asset_item

            for row, (property_key, property_value, property_default) in enumerate(
                properties
            ):
                col_property_name = QTableWidgetItem(property_key)
                col_property_name.setFlags(
                    Qt.ItemIsEnabled
                )  # Make the property name read-only

                col_value = QTableWidgetItem(property_value)
                col_value.setFlags(
                    Qt.ItemIsEditable | Qt.ItemIsEnabled
                )  # Make the value editable

                col_default_value = QTableWidgetItem(property_default)
                col_default_value.setFlags(
                    Qt.ItemIsEnabled
                )  # Make the default value read-only

                self.properties_table.setItem(row, 0, col_property_name)
                self.properties_table.setItem(row, 1, col_value)
                self.properties_table.setItem(row, 2, col_default_value)

            # Set the item delegate and pass asset_item - based on Andrei's input
            self.properties_table.setItemDelegateForColumn(
                1, EditableDelegate(asset_item)
            )

        else:
            self.properties_table.currentItem = None

    def update_attack_steps_window(self, selected_item: AttackerItem | AssetItem | None):
        if isinstance(selected_item, AttackerItem):
            self.attack_steps_docked_window.clear()
            for attack_step_name in selected_item.entry_points:
                self.attack_steps_docked_window.addItem(attack_step_name)
            return

        if isinstance(selected_item, AssetItem):
            self.attack_steps_docked_window.clear()
            for attack_step in selected_item.asset.lg_asset.attack_steps.values():
                self.attack_steps_docked_window.addItem(attack_step.name)
            return

        else:
            self.attack_steps_docked_window.clear()

    def update_asset_relations_window(self, asset_item):
        self.asset_relations_docker_window.clear()

        if asset_item is None:
            return

        asset: ModelAsset = asset_item.asset
        for fieldname, assets in asset.associated_assets.items():
            for associated_asset in assets:
                self.asset_relations_docker_window.addItem(
                    fieldname + "-->" + associated_asset.name
                )

    def create_actions(self, scene: ModelScene):
        """Create the actions and add to the GUI"""
        zoom_in_icon = image_path("zoomIn.png")
        self.zoom_in_action = QAction(QIcon(zoom_in_icon), "ZoomIn", self)
        self.zoom_in_action.triggered.connect(self.zoom_in)

        zoom_out_icon = image_path("zoomOut.png")
        self.zoom_out_action = QAction(QIcon(zoom_out_icon), "ZoomOut", self)
        self.zoom_out_action.triggered.connect(self.zoom_out)

        undo_icon = image_path("undoIcon.png")
        self.undo_action = QAction(QIcon(undo_icon), "Undo", self)
        self.undo_action.setShortcut("Ctrl+z")
        self.undo_action.triggered.connect(scene.undo_stack.undo)

        redo_icon = image_path("redoIcon.png")
        self.redo_action = QAction(QIcon(redo_icon), "Redo", self)
        self.redo_action.setShortcut("Ctrl+Shift+z")
        self.redo_action.triggered.connect(scene.undo_stack.redo)

        cut_icon = image_path("cutIcon.png")
        self.cut_action = QAction(QIcon(cut_icon), "Cut", self)
        self.cut_action.setShortcut("Ctrl+x")
        self.cut_action.triggered.connect(
            lambda: self.scene.cut_assets(scene.selectedItems())
        )

        copy_icon = image_path("copyIcon.png")
        self.copy_action = QAction(QIcon(copy_icon), "Copy", self)
        self.copy_action.setShortcut("Ctrl+c")
        self.copy_action.triggered.connect(
            lambda: self.scene.copy_assets(scene.selectedItems())
        )

        paste_icon = image_path("pasteIcon.png")
        self.paste_action = QAction(QIcon(paste_icon), "Paste", self)
        self.paste_action.setShortcut("Ctrl+v")
        self.paste_action.triggered.connect(
            lambda: self.scene.paste_assets(QPointF(0, 0))
        )

        delete_icon = image_path("deleteIcon.png")
        self.delete_action = QAction(QIcon(delete_icon), "Delete", self)
        self.delete_action.setShortcut("Delete")
        self.delete_action.triggered.connect(
            lambda: self.scene.delete_assets(scene.selectedItems()))

        drag_icon = image_path("drag.png")
        self.hand_drag_action = QAction(QIcon(drag_icon),"Drag", self)
        self.hand_drag_action.setCheckable(True)
        self.hand_drag_action.setShortcut("Ctrl+d")
        self.hand_drag_action.setToolTip("Toggle drag-to-pan the view")
        self.hand_drag_action.toggled.connect(self.toggle_hand_drag)

        drag_icon = image_path("drag.png")
        self.hand_drag_action = QAction(QIcon(drag_icon),"Drag", self)
        self.hand_drag_action.setCheckable(True)
        self.hand_drag_action.setShortcut("Ctrl+d")
        self.hand_drag_action.setToolTip("Toggle drag-to-pan the view")
        self.hand_drag_action.toggled.connect(self.toggle_hand_drag)

    def create_menu_bar(self):
        """Create the menu and add to the GUI"""
        menu_bar = self.menuBar()

        self.file_menu = menu_bar.addMenu("&File")
        self.file_menu_new_action = self.file_menu.addAction("New")
        self.file_menu_open_action = self.file_menu.addAction("Load Model/Scenario")
        self.file_menu_quick_load_action = self.file_menu.addAction("Reload Current File")
        self.file_menu_reload_project_action = self.file_menu.addAction("Reload Project")
        self.file_menu_save_action = self.file_menu.addAction("Save Current File")
        self.file_menu_save_as_action = self.file_menu.addAction("Export Model..")
        self.file_menu_export_scenario_action = self.file_menu.addAction(
            "Export Scenario.."
        )
        self.file_menu_save_as_drawio = self.file_menu.addAction(
            "Export draw.io file.."
        )
        self.file_menu_quit_action = self.file_menu.addAction("Quit")
        self.file_menu_open_action.triggered.connect(self.load_model_or_scenario)
        self.file_menu_quit_action.setShortcut("Ctrl+q")
        self.file_menu_save_action.setShortcut("Ctrl+s")
        self.file_menu_quick_load_action.setShortcut("Ctrl+r")
        self.file_menu_reload_project_action.setShortcut("Ctrl+Shift+r")
        self.file_menu_quick_load_action.triggered.connect(self.quick_load_current_file)
        self.file_menu_reload_project_action.triggered.connect(self.reload_project_from_mal)
        self.file_menu_save_action.triggered.connect(self.save_current_file)
        self.file_menu_save_as_action.triggered.connect(self.save_as_model)
        self.file_menu_export_scenario_action.triggered.connect(self.save_as_scenario)
        self.file_menu_save_as_drawio.triggered.connect(self.save_as_drawio)
        self.file_menu_quit_action.triggered.connect(self.quitApp)
        self.update_scenario_save_action_state()

        self.edit_menu = menu_bar.addMenu("Edit")
        self.edit_menu_undo_action = self.edit_menu.addAction(self.undo_action)
        self.edit_menu_redo_action = self.edit_menu.addAction(self.redo_action)
        self.edit_menu_cut_action = self.edit_menu.addAction(self.cut_action)
        self.edit_menu_copy_action = self.edit_menu.addAction(self.copy_action)
        self.edit_menu_paste_action = self.edit_menu.addAction(self.paste_action)
        self.edit_menu_delete_action = self.edit_menu.addAction(self.delete_action)

        return menu_bar

    def create_toolbar(self):
        """Create the toolbar and add to the GUI"""

        toolbar = QToolBar("Mainwindow Toolbar")

        # Adjust the size to reduce bigger image - its a magic number
        toolbar.setIconSize(QSize(20, 20))

        # Set the style to show text beside the icon for the entire toolbar
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        toolbar.addAction(self.file_menu_quit_action)
        toolbar.addSeparator()

        show_association_checkbox_label = QLabel("Show Association")
        show_association_checkbox = QCheckBox()
        show_association_checkbox.setCheckState(Qt.CheckState.Unchecked)
        toolbar.addWidget(show_association_checkbox_label)
        toolbar.addWidget(show_association_checkbox)
        show_association_checkbox.stateChanged.connect(
            self.show_association_checkbox_changed
        )

        toolbar.addSeparator()

        show_image_icon_checkbox_label = QLabel("Show Image Icon")
        show_image_icon_checkbox = QCheckBox()
        show_image_icon_checkbox.setCheckState(Qt.CheckState.Checked)
        toolbar.addWidget(show_image_icon_checkbox_label)
        toolbar.addWidget(show_image_icon_checkbox)
        show_image_icon_checkbox.stateChanged.connect(
            self.show_image_icon_checkbox_changed
        )

        toolbar.addSeparator()

        toolbar.addAction(self.hand_drag_action)
        toolbar.addAction(self.zoom_in_action)
        toolbar.addAction(self.zoom_out_action)
        self.zoom_label = QLabel("100%")
        self.zoom_line_edit = QLineEdit()

        # No limit on zoom level, but should be an integer
        self.zoom_line_edit.setValidator(QIntValidator())
        self.zoom_line_edit.setText("100")
        self.zoom_line_edit.returnPressed.connect(self.set_zoom_level_from_line_edit)
        self.zoom_line_edit.setFixedWidth(40)
        toolbar.addWidget(self.zoom_label)
        toolbar.addWidget(self.zoom_line_edit)
        toolbar.addSeparator()
        toolbar.addAction(self.undo_action)
        toolbar.addAction(self.redo_action)
        toolbar.addSeparator()
        toolbar.addAction(self.cut_action)
        toolbar.addAction(self.copy_action)
        toolbar.addAction(self.paste_action)
        toolbar.addAction(self.delete_action)
        toolbar.addSeparator()
        fit_to_view_icon = image_path("fitToView.png")
        fit_to_view_button = QPushButton(QIcon(fit_to_view_icon), "Fit To View")
        toolbar.addWidget(fit_to_view_button)
        fit_to_view_button.clicked.connect(self.fit_to_view_button_clicked)
        toolbar.addSeparator()

        # Material Theme - https://pypi.org/project/qt-material/
        material_theme_label = QLabel("Theme")
        self.theme_combo_box = QComboBox()

        self.theme_combo_box.addItem("None")
        inbuilt_theme_list_from_package = list_themes()
        self.theme_combo_box.addItems(inbuilt_theme_list_from_package)

        toolbar.addWidget(material_theme_label)
        toolbar.addWidget(self.theme_combo_box)
        self.theme_combo_box.currentIndexChanged.connect(self.on_theme_selection_change)
        toolbar.addSeparator()
        return toolbar

    def zoom_in(self):
        """Called on zoom in button click"""
        print("Zoom In Clicked")
        self.view.zoomIn()

    def zoom_out(self):
        """Called on zoom out button click"""
        print("Zoom Out Clicked")
        self.view.zoomOut()

    def set_zoom_level_from_line_edit(self):
        """Set zoom label to match current zoom factor"""
        zoomValue = int(self.zoom_line_edit.text())
        self.view.set_zoom(zoomValue)

    def toggle_hand_drag(self, checked: bool):
        """Enable or disable drag-to-pan in the view."""
        self.view.set_hand_drag_enabled(checked)

    def update_zoom_label(self):
        """Set zoom label to match current zoom factor"""
        self.zoom_label.setText(f"{int(self.view.zoom_factor * 100)}%")
        self.zoom_line_edit.setText(f"{int(self.view.zoom_factor * 100)}")

    def load_model_or_scenario(self):
        """Load a file, either model or scenario"""
        file_extension_filter = "YAML Files (*.yaml *.yml);;JSON Files (*.json)"
        file_path, _ = QFileDialog.getOpenFileName(
            None, "Select model or scenario File", "", file_extension_filter
        )

        if not file_path:
            print("No valid path detected for loading")
            self.show_error_popup("No valid path detected for loading")
            return

        open_project_user_confirmation = QMessageBox.question(
            self,
            "Load New Project",
            "Loading a new project will delete current work (if any). "
            "Do you want to continue ?",
            QMessageBox.Ok | QMessageBox.Cancel,
        )

        if open_project_user_confirmation == QMessageBox.Ok:
            # clear scene so that canvas becomes blank
            self.scene.clear()
            try:
                self.load_model(file_path)
                print(f"Loaded model from {file_path}")
            except ModelException:
                self.load_scenario(file_path)
                print(f"Loaded scenario from {file_path}")
        else:
            print("User cancelled 'Load'")
            return

    def quick_load_current_file(self):
        """Reload currently loaded model or scenario from file."""
        file_path = self.scenario_file_name or self.model_file_name
        if not file_path:
            self.show_error_popup("No loaded file to quick load")
            return

        quick_load_user_confirmation = QMessageBox.question(
            self,
            "Quick Load",
            "Quick Load will discard current unsaved changes. "
            "Do you want to continue?",
            QMessageBox.Ok | QMessageBox.Cancel
        )

        if quick_load_user_confirmation != QMessageBox.Ok:
            return

        self.scene.clear()
        try:
            if self.scenario_file_name:
                self.load_scenario(file_path)
                print(f"Quick loaded scenario from {file_path}")
            else:
                self.load_model(file_path)
                print(f"Quick loaded model from {file_path}")
        except Exception as e:
            self.show_error_popup(f"Could not quick load file: {e}")

    def reload_project_from_mal(self):
        """Reload the current MAL project and reopen the active file if possible."""
        if not self.lang_file_path:
            self.show_error_popup("No loaded MAL language file to reload")
            return

        quick_load_user_confirmation = QMessageBox.question(
            self,
            "Reload Project",
            "Reloading the MAL project will discard current unsaved changes. "
            "Do you want to continue?",
            QMessageBox.Ok | QMessageBox.Cancel
        )

        if quick_load_user_confirmation != QMessageBox.Ok:
            return

        try:
            self.reload_current_project()
            print("Reloaded current project")
        except Exception as e:
            self.show_error_popup(f"Could not reload MAL language file: {e}")

    def reload_current_project(self):
        """Reload the current MAL file and reopen the current model/scenario."""
        scenario_file_path = self.scenario_file_name
        model_file_path = self.model_file_name

        self.load_empty_project(self.lang_file_path)

        if scenario_file_path:
            try:
                self.load_scenario(scenario_file_path)
            except Exception as e:
                self.show_error_popup(
                    "Could not reload scenario file; opened empty project "
                    f"instead: {e}"
                )
            return

        if model_file_path:
            try:
                self.load_model(model_file_path)
            except Exception as e:
                self.show_error_popup(
                    "Could not reload model file; opened empty project "
                    f"instead: {e}"
                )

    def load_empty_project(self, lang_file_path: str):
        """Reload the MAL language and reset the window to an empty project."""
        lang_file_path = _path_to_str(lang_file_path)
        lang_graph = LanguageGraph.load_from_file(lang_file_path)
        self._loaded_meta_detector_data = []
        self.load_scene(lang_file_path, Model("New Model", lang_graph))
        self.model_file_name = None
        self.scenario_file_name = None
        if hasattr(self, "_lang_file"):
            delattr(self, "_lang_file")
        self.update_scenario_save_action_state()

    def load_scenario(self, file_path: str):
        """Load model and agents from a scenario"""
        file_path = _path_to_str(file_path)
        self._loaded_meta_detector_data = self._load_meta_detectors_from_model_file(
            file_path
        )
        scenario, lang_file_path = self._load_scenario_from_file(file_path)
        # Reload in case language was changed
        self.load_scene(lang_file_path, scenario.model, scenario)
        self.model_file_name = None
        self.scenario_file_name = file_path
        self._lang_file = lang_file_path
        self.update_scenario_save_action_state()

    def _load_scenario_from_file(self, file_path: str):
        file_path = _path_to_str(file_path)
        with open(file_path, "r", encoding="utf-8") as file_obj:
            scenario_dict = yaml.safe_load(file_obj) or {}

        lang_file_path = self._resolve_scenario_lang_file(
            file_path, scenario_dict.get("lang_file")
        )
        scenario_dict["lang_file"] = lang_file_path
        return Scenario.from_dict(scenario_dict), lang_file_path

    def _resolve_scenario_lang_file(
        self, scenario_file_path: str, scenario_lang_file: str | None
    ) -> str:
        scenario_file_path = _path_to_str(scenario_file_path)
        if not scenario_lang_file:
            return self.lang_file_path

        scenario_path = Path(scenario_file_path).resolve()
        lang_path = Path(scenario_lang_file)
        if not lang_path.is_absolute():
            lang_path = scenario_path.parent / lang_path
        lang_path = lang_path.resolve()

        if lang_path == scenario_path:
            return self.lang_file_path

        try:
            LanguageGraph.load_from_file(str(lang_path))
        except Exception:
            return self.lang_file_path
        return str(lang_path)

    def _scenario_agent_settings_by_type(self):
        if not self.scene.scenario:
            return {}, {}

        if hasattr(self.scene.scenario, "attacker_settings") and hasattr(
            self.scene.scenario, "defender_settings"
        ):
            return (
                self.scene.scenario.attacker_settings,
                self.scene.scenario.defender_settings,
            )

        agent_settings = getattr(self.scene.scenario, "agent_settings", {})
        if not isinstance(agent_settings, dict):
            return {}, {}

        attacker_agents = {
            name: agent
            for name, agent in agent_settings.items()
            if isinstance(agent, AttackerSettings)
        }
        defender_agents = {
            name: agent
            for name, agent in agent_settings.items()
            if isinstance(agent, DefenderSettings)
        }
        return attacker_agents, defender_agents

    def _create_scenario(self, agents):
        scenario_args = {
            "lang_file": self.lang_file_path,
            "model": self.scene.model,
        }
        if "agents" in inspect.signature(Scenario).parameters:
            scenario_args["agents"] = tuple(agents)
        else:
            scenario_args["agent_settings"] = {agent.name: agent for agent in agents}
        return Scenario(**scenario_args)

    def load_model(self, file_path: str):
        """Load a MAL model from a file"""
        file_path = _path_to_str(file_path)
        self._loaded_meta_detector_data = self._load_meta_detectors_from_model_file(
            file_path
        )
        model = Model.load_from_file(file_path, self.scene.lang_graph)
        self.load_scene(self.lang_file_path, model)
        self.scenario_file_name = None
        self.model_file_name = file_path
        if hasattr(self, "_lang_file"):
            delattr(self, "_lang_file")
        self.update_scenario_save_action_state()

    def update_scenario_save_action_state(self):
        """Enable save action only when a loaded scenario file is available."""
        if hasattr(self, "file_menu_save_action"):
            self.file_menu_save_action.setEnabled(
                bool(self.scenario_file_name or self.model_file_name)
            )
        if hasattr(self, "file_menu_quick_load_action"):
            self.file_menu_quick_load_action.setEnabled(
                bool(self.scenario_file_name or self.model_file_name)
            )
        if hasattr(self, "file_menu_reload_project_action"):
            self.file_menu_reload_project_action.setEnabled(bool(self.lang_file_path))

    def save_current_file(self):
        """Save the currently loaded scenario or model."""
        if self.scenario_file_name:
            self.save_scenario()
            return
        if self.model_file_name:
            self.save_model()
            return
        self.show_error_popup("No loaded file to save")

    def add_positions_to_model(self):
        """Add GUI-specific save metadata to model assets."""
        for asset in self.scene.model.assets.values():
            print(f"ASSET NAME:{asset.name} ID:{asset.id} TYPE:{asset.type}")
            item = self.scene._asset_id_to_item[int(asset.id)]
            position = item.pos()

            extras_dict = dict(asset.extras or {})
            extras_dict["position"] = {"x": position.x(), "y": position.y()}
            asset.extras = extras_dict

        self._add_attackers_to_model_metadata()

    def _serialize_attacker_items(self) -> list[dict]:
        return [
            {
                "kind": getattr(attacker_item, "ITEM_KIND", "attacker"),
                "name": attacker_item.name,
                "entry_points": list(attacker_item.entry_points),
                "goals": list(attacker_item.goals),
                "policy": attacker_item.policy.__name__,
                "position": {
                    "x": attacker_item.pos().x(),
                    "y": attacker_item.pos().y(),
                },
            }
            for attacker_item in self.scene.attacker_items
            if getattr(attacker_item, "ITEM_KIND", "attacker") == "attacker"
        ]

    def _serialize_meta_detector_items(self) -> dict[int, dict]:
        serialized_meta_detectors = {}
        for index, meta_detector_item in enumerate(
            (
                item
                for item in self.scene.attacker_items
                if getattr(item, "ITEM_KIND", "attacker") == "meta_detector"
            ),
            start=1,
        ):
            associated_assets = {}
            associated_asset_labels = {}
            for asset_name in meta_detector_item.connected_assets:
                asset = self.scene.model.get_asset_by_name(asset_name)
                if asset:
                    associated_assets[asset.id] = asset.name
                    label_value = meta_detector_item.connected_asset_labels.get(
                        asset.name, 1
                    )
                    associated_asset_labels[asset.id] = label_value

            serialized_meta_detectors[index] = {
                "associated_assets": associated_assets,
                "extras": {
                    "position": {
                        "x": meta_detector_item.pos().x(),
                        "y": meta_detector_item.pos().y(),
                    }
                },
                "name": meta_detector_item.name,
            }
            serialized_meta_detectors[index][
                "associated_asset_labels"
            ] = associated_asset_labels

        return serialized_meta_detectors

    def _add_attackers_to_model_metadata(self):
        for asset in self.scene.model.assets.values():
            extras_dict = dict(asset.extras or {})
            extras_dict.pop(self.ATTACKER_METADATA_KEY, None)
            asset.extras = extras_dict

        attacker_metadata = self._serialize_attacker_items()
        if not attacker_metadata or not self.scene.model.assets:
            return

        anchor_asset = min(self.scene.model.assets.values(), key=lambda asset: asset.id)
        extras_dict = dict(anchor_asset.extras or {})
        extras_dict[self.ATTACKER_METADATA_KEY] = attacker_metadata
        anchor_asset.extras = extras_dict

    def _write_meta_detectors_to_model_file(self, file_path: str):
        file_path = _path_to_str(file_path)
        if not Path(file_path).exists():
            return

        with open(file_path, "r", encoding="utf-8") as file_obj:
            model_dict = yaml.safe_load(file_obj) or {}
        model_section = dict(model_dict.get("model") or {})
        meta_detector_data = self._serialize_meta_detector_items()

        if meta_detector_data:
            model_section[self.META_DETECTORS_MODEL_KEY] = meta_detector_data
        else:
            model_section.pop(self.META_DETECTORS_MODEL_KEY, None)

        if model_section:
            model_dict["model"] = model_section
        else:
            model_dict.pop("model", None)

        with open(file_path, "w", encoding="utf-8") as file_obj:
            yaml.safe_dump(model_dict, file_obj, sort_keys=False)

    def _load_meta_detectors_from_model_file(self, file_path: str) -> list[dict]:
        file_path = _path_to_str(file_path)
        with open(file_path, "r", encoding="utf-8") as file_obj:
            model_dict = yaml.safe_load(file_obj) or {}
        model_section = model_dict.get("model") or {}
        meta_detectors = model_section.get(self.META_DETECTORS_MODEL_KEY) or {}

        loaded_meta_detectors = []
        for meta_detector_info in meta_detectors.values():
            associated_assets = meta_detector_info.get("associated_assets") or {}
            associated_asset_labels = (
                meta_detector_info.get("associated_asset_labels") or {}
            )
            position = (meta_detector_info.get("extras") or {}).get("position") or {}
            connection_labels = {}
            for asset_id, asset_name in associated_assets.items():
                try:
                    label_value = associated_asset_labels.get(
                        asset_id, associated_asset_labels.get(str(asset_id), 1)
                    )
                except AttributeError:
                    label_value = 1
                connection_labels[asset_name] = int(label_value)
            loaded_meta_detectors.append(
                {
                    "name": meta_detector_info.get("name", "Meta Detector"),
                    "connections": list(associated_assets.values()),
                    "connection_labels": connection_labels,
                    "position": {
                        "x": position.get("x", 0),
                        "y": position.get("y", 0),
                    },
                }
            )

        return loaded_meta_detectors

    def save_model(self):
        """Save to file if filename set, else save as new file"""
        if self.model_file_name:
            file_path = _path_to_str(self.model_file_name)
            self.add_positions_to_model()
            self.scene.model.save_to_file(file_path)
            self._write_meta_detectors_to_model_file(file_path)
        else:
            self.save_as_model()

    def save_as_model(self):
        """`Save as`. Let user select target file and save model."""
        self.add_positions_to_model()
        file_dialog = QFileDialog()
        file_dialog.setAcceptMode(QFileDialog.AcceptSave)
        file_dialog.setDefaultSuffix("yaml")
        file_path, _ = file_dialog.getSaveFileName()

        if not file_path:
            print("No valid path detected for saving")
            return
        else:
            self.scene.model.name = Path(file_path).stem
            self.model_file_name = file_path
            try:
                file_path = _path_to_str(file_path)
                self.scene.model.save_to_file(file_path)
                self._write_meta_detectors_to_model_file(file_path)
            except Exception as e:
                print(f"Error saving model: {e}")
                self.show_error_popup("Error saving model: " + str(e))
                self.model_file_name = None
                return

    def save_as_drawio(self):
        """`Save as`. Let user select target file and save .drawio file."""

        def versiontuple(v):
            return tuple(map(int, (v.split("."))))

        if versiontuple(maltoolbox_version) <= versiontuple("1.0.6"):
            self.show_error_popup(
                "Your version of maltoolbox needs to be > 1.0.6 for this feature"
            )
            return

        # For backwards compatibility we import here instead
        from maltoolbox.visualization import create_drawio_file_with_images

        file_dialog = QFileDialog()
        file_dialog.setAcceptMode(QFileDialog.AcceptSave)
        file_dialog.setDefaultSuffix("drawio")
        default_name = self.scene.model.name + ".drawio"
        file_path, _ = file_dialog.getSaveFileName(
            None,
            "Save As Draw.io file",
            default_name,
            "DrawIO Files (*.drawio);;All Files (*)",
        )

        if not file_path:
            self.show_error_popup("No valid path detected for saving")
            return
        else:
            self.scene.model.name = Path(file_path).stem
            self.model_file_name = file_path
            try:
                self.add_positions_to_model()
                create_drawio_file_with_images(
                    self.scene.model, output_filename=file_path
                )
                self._add_detectors_to_drawio_file(file_path)
            except Exception as e:
                print(f"Error saving model: {e}")
                self.show_error_popup("Error saving model: " + str(e))
                self.model_file_name = None
                return

    def _add_detectors_to_drawio_file(
        self, file_path: str, coordinate_scale: float = 0.75
    ):
        """Append detector markers to a draw.io file exported by maltoolbox."""
        file_path = _path_to_str(file_path)
        tree = ET.parse(file_path)
        root = tree.getroot()
        root_cell = root.find("./diagram/mxGraphModel/root")
        if root_cell is None:
            return

        for asset in self.scene.model.assets.values():
            item = self.scene._asset_id_to_item.get(int(asset.id))
            if not item or not getattr(item, "has_detector", False):
                continue

            position = dict(asset.extras or {}).get("position") or {}
            x = round(position.get("x", item.pos().x()) * coordinate_scale)
            y = round(position.get("y", item.pos().y()) * coordinate_scale)
            self._append_drawio_detector_marker(root_cell, asset.id, x, y)

        rough_string = ET.tostring(root, "utf-8")
        reparsed = minidom.parseString(rough_string)
        pretty_xml = reparsed.toprettyxml(indent="  ")
        lines = [line for line in pretty_xml.split("\n") if line.strip()]
        with open(file_path, "w", encoding="utf-8") as file_obj:
            file_obj.write("\n".join(lines))

    def _append_drawio_detector_marker(self, root_cell, asset_id: int, x: int, y: int):
        detector_color = "#B41E1E"
        stroke_color = "#141414"
        stem = ET.SubElement(root_cell, "mxCell")
        stem.set("id", f"detector_{asset_id}_stem")
        stem.set(
            "style",
            "rounded=0;whiteSpace=wrap;html=1;"
            f"fillColor={detector_color};strokeColor={stroke_color};",
        )
        stem.set("vertex", "1")
        stem.set("parent", "1")

        stem_geometry = ET.SubElement(stem, "mxGeometry")
        stem_geometry.set("x", str(x + 112))
        stem_geometry.set("y", str(y - 12))
        stem_geometry.set("width", "4")
        stem_geometry.set("height", "42")
        stem_geometry.set("as", "geometry")

        diamond = ET.SubElement(root_cell, "mxCell")
        diamond.set("id", f"detector_{asset_id}_diamond")
        diamond.set(
            "style",
            "rhombus;whiteSpace=wrap;html=1;"
            f"fillColor={detector_color};strokeColor={stroke_color};",
        )
        diamond.set("vertex", "1")
        diamond.set("parent", "1")

        diamond_geometry = ET.SubElement(diamond, "mxGeometry")
        diamond_geometry.set("x", str(x + 107))
        diamond_geometry.set("y", str(y - 25))
        diamond_geometry.set("width", "14")
        diamond_geometry.set("height", "14")
        diamond_geometry.set("as", "geometry")

    def save_scenario(self):
        """Save loaded scenario back to its current file."""
        if not self.scenario_file_name:
            self.show_error_popup("No loaded scenario file to save")
            return
        self._save_scenario_to_file(self.scenario_file_name)

    def save_as_scenario(self):
        """`Save as`. Let user select target file and save scenario."""
        file_dialog = QFileDialog()
        file_dialog.setAcceptMode(QFileDialog.AcceptSave)
        file_dialog.setDefaultSuffix("yaml")
        file_path, _ = file_dialog.getSaveFileName()

        if not file_path:
            print("No valid path detected for saving")
            self.show_error_popup("No valid path detected for saving")
            return
        self._save_scenario_to_file(file_path)

    def _save_scenario_to_file(self, file_path: str):
        """Save scenario data to the provided path."""
        file_path = _path_to_str(file_path)
        prev_attacker_agents, prev_defender_agents = (
            self._scenario_agent_settings_by_type()
        )
        # Start with existing defender agents, as they are not editable in the GUI
        new_agents: list[AttackerSettings | DefenderSettings] = list(
            prev_defender_agents.values()
        )

        # Add attacker agents from scene
        for attacker_item in self.scene.attacker_items:
            if getattr(attacker_item, "ITEM_KIND", "attacker") != "attacker":
                continue

            prev_agent = prev_attacker_agents.get(attacker_item.name)

            if prev_agent:
                # If agent already exists in scenario, update entrypoints
                agent = AttackerSettings(
                    name=prev_agent.name,
                    entry_points=set(attacker_item.entry_points),
                    goals=set(attacker_item.goals),
                    type=AgentType.ATTACKER,
                    policy=attacker_item.policy,
                )
            else:
                # Otherwise, add new agent to scenario agents tuple
                agent = AttackerSettings(
                    name=attacker_item.name,
                    entry_points=set(attacker_item.entry_points),
                    goals=set(attacker_item.goals),
                    type=AgentType.ATTACKER,
                    policy=attacker_item.policy,
                )
            new_agents.append(agent)

        self.add_positions_to_model()

        try:
            scenario = self._create_scenario(new_agents)
            scenario.save_to_file(file_path)
            self._write_meta_detectors_to_model_file(file_path)

            if hasattr(self, "_lang_file"):
                with open(file_path, "r", encoding="utf-8") as file_obj:
                    scenario_dict = yaml.safe_load(file_obj)
                scenario_dict["lang_file"] = self._lang_file
                with open(file_path, "w", encoding="utf-8") as file_obj:
                    yaml.safe_dump(scenario_dict, file_obj, sort_keys=False)
        except Exception as e:
            self.show_error_popup("Could not save scenario: " + str(e))

    def quitApp(self):
        print("Quit")
        self.app.quit()

    def show_information_popup(self, message_text):
        """Show a popup with given message"""
        parent_widget = QWidget()  # To maintain object lifetim
        message_box = QMessageBox(parent_widget)
        message_box.setIcon(QMessageBox.Information)
        message_box.setWindowTitle("Information")
        message_box.setText("This is default informative Text")
        message_box.setInformativeText(message_text)
        message_box.setStandardButtons(QMessageBox.Ok)
        message_box.exec()

    def show_error_popup(self, message_text):
        """Show error popup with given message"""
        parent_widget = QWidget()  # To maintain object lifetim
        message_box = QMessageBox(parent_widget)
        message_box.setIcon(QMessageBox.Critical)
        message_box.setWindowTitle("Error")
        message_box.setInformativeText(message_text)
        message_box.setStandardButtons(QMessageBox.Ok)
        message_box.exec()

    def update_explorer_docked_window(self):
        """
        Clean the existing child and fill each items from scratch
        TODO performance BAD - To be discussed/improved
        """
        self.object_explorer_tree.clear_all_object_explorer_child_items()

        # Fill all the items from Scene one by one
        for child_asset_item in self.scene.items():
            if isinstance(child_asset_item, AssetItem):
                # Check if parent exists before adding child
                parent_item, parent_asset_type = (
                    self.object_explorer_tree.check_and_get_if_parent_asset_type_exists(
                        child_asset_item.asset_type
                    )
                )

                if parent_asset_type:
                    self.object_explorer_tree.add_child_item(
                        parent_item, child_asset_item, str(child_asset_item.asset_name)
                    )

    def on_theme_selection_change(self):
        """Set the selected theme"""
        selected_theme = self.theme_combo_box.currentText()
        print(f"{selected_theme} is the Theme selected")
        apply_stylesheet(self.app, theme=selected_theme)
