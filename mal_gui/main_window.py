from pathlib import Path
from typing import Any, Optional

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
    QApplication
)
from PySide6.QtGui import QDrag, QAction, QIcon, QIntValidator
from PySide6.QtCore import Qt, QMimeData, QByteArray, QSize, Signal, QPointF

from qt_material import apply_stylesheet,list_themes

from maltoolbox import __version__ as maltoolbox_version
from maltoolbox.language import LanguageGraph
from maltoolbox.model import Model, ModelAsset
from maltoolbox.exceptions import ModelException
from malsim.config.agent_settings import AttackerSettings, AgentType
from malsim.scenario import Scenario
from malsim.policies import RandomAgent

from .file_utils import image_path
from .model_scene import ModelScene
from .model_view import ModelView
from .object_explorer import AssetItem, AssetFactory
from .assets_container.assets_container import AssetsContainer
from .connection_item import AssociationConnectionItem
from .docked_windows import (
    DraggableTreeView,
    ItemDetailsWindow,
    PropertiesWindow,
    EditableDelegate,
    AttackStepsWindow,
    AssetRelationsWindow
)

# Used to create absolute paths of assets
PACKAGE_DIR = Path(__file__).resolve().parent

class DraggableListWidget(QListWidget):
    def mousePressEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            item = self.itemAt(event.position().toPoint())
            if item:
                drag = QDrag(self)
                mime_data = QMimeData()
                mime_data.setData(
                    "application/x-qabstractitemmodeldatalist", QByteArray())
                mime_data.setData("text/plain", item.text().encode())
                drag.setMimeData(mime_data)
                drag.exec()


class MainWindow(QMainWindow):
    update_childs_in_object_explorer_signal = Signal()

    def __init__(self, app: QApplication, lang_file_path: str):
        super().__init__()
        self.setWindowTitle("MAL GUI")
        self.app = app # declare an app member

        self.scenario_file_name = None
        self.model_file_name = None

        self.lang_file_path = lang_file_path
        lang_graph = LanguageGraph.load_from_file(lang_file_path)
        self.asset_factory = self.create_asset_factory(lang_graph)
        self.scene = self.create_scene(
            lang_graph, self.asset_factory, Model("New Model", lang_graph)
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
            self,
            lang_file_path: str,
            model: Model,
            scenario: Optional[Scenario] = None
        ):
        """Load scene with given language and model"""
        print("LOADING SCENE!")
        self.clear_window()
        self.lang_file_path = lang_file_path
        lang_graph = LanguageGraph.load_from_file(lang_file_path)
        self.asset_factory = self.create_asset_factory(lang_graph)
        self.scene = self.create_scene(
            lang_graph, self.asset_factory, model, scenario
        )

        self.create_menu_bar()
        self.create_actions(self.scene)
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
            "User": image_path("user.png")
        }

        # Create a registry as a dictionary containing
        # name as key and class as value
        asset_factory = AssetFactory()
        asset_factory.register_asset(
            "Attacker", image_path("attacker.png")
        )

        for asset in lang_graph.assets.values():
            if not asset.is_abstract:
                asset_factory.register_asset(
                    asset.name,
                    asset_images.get(asset.name, image_path('unknown.png'))
                )

        return asset_factory

    def create_scene(
            self,
            lang_graph: LanguageGraph,
            asset_factory: AssetFactory,
            model: Model,
            scenario: Optional[Scenario] = None
        ):
        """Create and initialize scene from language"""

        model_scene = ModelScene(
            asset_factory, lang_graph, model, self, scenario
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
            self.scene,
            eye_unhide_icon_image,
            eye_hide_icon_image,
            rgb_color_icon_image
        )

        for _, values in asset_factory.asset_registry.items():
            for value in values:
                self.object_explorer_tree.set_parent_item_text(
                    value.asset_type, value.asset_image
                )

        dock_object_explorer.setWidget(self.object_explorer_tree)
        self.addDockWidget(Qt.LeftDockWidgetArea, dock_object_explorer)
        dock_widgets.append(dock_object_explorer)

        #EDOC Tab with treeview
        component_tab_tree = QTreeWidget()
        component_tab_tree.setHeaderLabel(None)

        #ItemDetails with treeview
        self.item_details_window = ItemDetailsWindow()
        dock_item_details = QDockWidget("Item Details",self)
        dock_item_details.setWidget(self.item_details_window)
        self.addDockWidget(Qt.LeftDockWidgetArea, dock_item_details)
        dock_widgets.append(dock_item_details)

        #Properties Tab with tableview
        self.properties_docked_window = PropertiesWindow()
        self.properties_table = self.properties_docked_window.properties_table
        dock_properties = QDockWidget("Properties",self)
        dock_properties.setWidget(self.properties_table)
        self.addDockWidget(Qt.LeftDockWidgetArea, dock_properties)
        dock_widgets.append(dock_properties)

        #AttackSteps Tab with ListView
        self.attack_steps_docked_window = AttackStepsWindow()
        dock_attack_steps = QDockWidget("Attack Steps",self)
        dock_attack_steps.setWidget(self.attack_steps_docked_window)
        self.addDockWidget(Qt.LeftDockWidgetArea, dock_attack_steps)
        dock_widgets.append(dock_attack_steps)

        #AssetRelations Tab with ListView
        self.asset_relations_docker_window = AssetRelationsWindow()
        dock_asset_relations = QDockWidget("Asset Relations",self)
        dock_asset_relations.setFeatures(QDockWidget.DockWidgetFloatable | 
                                         QDockWidget.DockWidgetMovable)
        dock_asset_relations.setWidget(self.asset_relations_docker_window)
        self.addDockWidget(Qt.LeftDockWidgetArea, dock_asset_relations)
        dock_widgets.append(dock_asset_relations)

        #Keep Propeties Window and Attack Step Window Tabbed
        self.tabifyDockWidget(dock_properties, dock_attack_steps)

        #Keep the properties Window highlighted and raised
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
            if isinstance(item, (AssetItem,AssetsContainer)):
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
                if attack_step.ttc and len(attack_step.ttc['arguments']) > 0:
                    default_value = attack_step.ttc['arguments'][0]
                else:
                    default_value = 0.0
                properties.append((attack_step_name, str(value), str(default_value)))

            for attack_step in asset.lg_asset.attack_steps.values():
                # Add defenses that are not set in model
                if attack_step.name in asset.defenses:
                    continue
                if attack_step.type == "defense":
                    if attack_step.ttc and len(attack_step.ttc['arguments']) > 0:
                        default_value = attack_step.ttc['arguments'][0]
                    else:
                        default_value = 0.0
                    properties.append((attack_step.name, "", str(default_value)))

            # Insert new rows based on the data dictionary
            num_rows = len(properties)
            self.properties_table.setRowCount(num_rows)
            self.properties_table.currentItem = asset_item

            for row, (property_key, property_value, property_default) in enumerate(properties):
                col_property_name = QTableWidgetItem(property_key)
                col_property_name.setFlags(Qt.ItemIsEnabled)  # Make the property name read-only

                col_value = QTableWidgetItem(property_value)
                col_value.setFlags(Qt.ItemIsEditable | Qt.ItemIsEnabled)  # Make the value editable

                col_default_value = QTableWidgetItem(property_default)
                col_default_value.setFlags(Qt.ItemIsEnabled)  # Make the default value read-only

                self.properties_table.setItem(row, 0, col_property_name)
                self.properties_table.setItem(row, 1, col_value)
                self.properties_table.setItem(row, 2, col_default_value)

            # Set the item delegate and pass asset_item - based on Andrei's input
            self.properties_table.setItemDelegateForColumn(1, EditableDelegate(asset_item))

        else:
            self.properties_table.currentItem = None

    def update_attack_steps_window(self, attacker_asset_item):
        if attacker_asset_item is not None:
            self.attack_steps_docked_window.clear()
            for asset, attack_step_names in \
                    attacker_asset_item.attackerAttachment.entry_points:
                for attack_step_name in attack_step_names:
                    self.attack_steps_docked_window.addItem(
                        asset.name + ':' + attack_step_name
                    )
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
            lambda: self.scene.cut_assets(scene.selectedItems()))

        copy_icon = image_path("copyIcon.png")
        self.copy_action = QAction(QIcon(copy_icon), "Copy", self)
        self.copy_action.setShortcut("Ctrl+c")
        self.copy_action.triggered.connect(
            lambda: self.scene.copy_assets(scene.selectedItems()))

        paste_icon = image_path("pasteIcon.png")
        self.paste_action = QAction(QIcon(paste_icon), "Paste", self)
        self.paste_action.setShortcut("Ctrl+v")
        self.paste_action.triggered.connect(
            lambda: self.scene.paste_assets(QPointF(0,0)))

        delete_icon = image_path("deleteIcon.png")
        self.delete_action = QAction(QIcon(delete_icon), "Delete", self)
        self.delete_action.setShortcut("Delete")
        self.delete_action.triggered.connect(
            lambda: self.scene.delete_assets(scene.selectedItems()))

    def create_menu_bar(self):
        """Create the menu and add to the GUI"""
        menu_bar = self.menuBar()

        self.file_menu = menu_bar.addMenu("&File")
        self.file_menu_new_action = self.file_menu.addAction("New")
        self.file_menu_open_action = self.file_menu.addAction("Load Model/Scenario")
        self.file_menu_save_as_action = self.file_menu.addAction("Export Model..")
        self.file_menu_export_scenario_action = self.file_menu.addAction("Export Scenario..")
        self.file_menu_save_as_drawio = self.file_menu.addAction("Export draw.io file..")
        self.file_menu_quit_action = self.file_menu.addAction("Quit")
        self.file_menu_open_action.triggered.connect(self.load_model_or_scenario)
        self.file_menu_save_as_action.triggered.connect(self.save_as_model)
        self.file_menu_export_scenario_action.triggered.connect(self.save_as_scenario)
        self.file_menu_save_as_drawio.triggered.connect(self.save_as_drawio)
        self.file_menu_quit_action.triggered.connect(self.quitApp)

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
            self.show_association_checkbox_changed)

        toolbar.addSeparator()

        show_image_icon_checkbox_label  = QLabel("Show Image Icon")
        show_image_icon_checkbox = QCheckBox()
        show_image_icon_checkbox.setCheckState(Qt.CheckState.Checked)
        toolbar.addWidget(show_image_icon_checkbox_label)
        toolbar.addWidget(show_image_icon_checkbox)
        show_image_icon_checkbox.stateChanged\
            .connect(self.show_image_icon_checkbox_changed)

        toolbar.addSeparator()

        toolbar.addAction(self.zoom_in_action)
        toolbar.addAction(self.zoom_out_action)
        self.zoom_label = QLabel("100%")
        self.zoom_line_edit = QLineEdit()

        # No limit on zoom level, but should be an integer
        self.zoom_line_edit.setValidator(QIntValidator())
        self.zoom_line_edit.setText("100")
        self.zoom_line_edit.returnPressed.connect(
            self.set_zoom_level_from_line_edit)
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
        fit_to_view_button = QPushButton(
            QIcon(fit_to_view_icon), "Fit To View")
        toolbar.addWidget(fit_to_view_button)
        fit_to_view_button.clicked.connect(self.fit_to_view_button_clicked)
        toolbar.addSeparator()

        #Material Theme - https://pypi.org/project/qt-material/
        material_theme_label  = QLabel("Theme")
        self.theme_combo_box = QComboBox()

        self.theme_combo_box.addItem('None')
        inbuilt_theme_list_from_package = list_themes()
        self.theme_combo_box.addItems(inbuilt_theme_list_from_package)

        toolbar.addWidget(material_theme_label)
        toolbar.addWidget(self.theme_combo_box)
        self.theme_combo_box.currentIndexChanged.connect(
            self.on_theme_selection_change
        )
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

    def update_zoom_label(self):
        """Set zoom label to match current zoom factor"""
        self.zoom_label.setText(f"{int(self.view.zoom_factor * 100)}%")
        self.zoom_line_edit.setText(f"{int(self.view.zoom_factor * 100)}")

    def load_model_or_scenario(self):
        """Load a file, either model or scenario"""
        file_extension_filter = \
            "YAML Files (*.yaml *.yml);;JSON Files (*.json)"
        file_path, _ = QFileDialog.getOpenFileName(
            None, "Select model or scenario File", "", file_extension_filter)

        if not file_path:
            print("No valid path detected for loading")
            return

        open_project_user_confirmation = QMessageBox.question(
            self,
            "Load New Project",
            "Loading a new project will delete current work (if any). "
            "Do you want to continue ?",
            QMessageBox.Ok | QMessageBox.Cancel
        )

        if open_project_user_confirmation == QMessageBox.Ok:
            #clear scene so that canvas becomes blank
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


    def load_scenario(self, file_path: str):
        """Load model and agents from a scenario"""
        scenario = Scenario.load_from_file(file_path)
        # Reload in case language was changed
        self.load_scene(scenario._lang_file, scenario.model, scenario)
        self.scenario_file_name = file_path

    def load_model(self, file_path: str):
        """Load a MAL model from a file"""

        self.model_file_name = file_path
        self.scene.model = Model.load_from_file(
            file_path, self.scene.lang_graph
        )

    def add_positions_to_model(self):
        """Add x/y positions to asset extras of model"""
        for asset in self.scene.model.assets.values():
            print(f'ASSET NAME:{asset.name} ID:{asset.id} TYPE:{asset.type}')
            item = self.scene._asset_id_to_item[int(asset.id)]
            position = item.pos()

            extras_dict = asset.extras if asset.extras else {}
            extras_dict["position"] = {
                "x": position.x(),
                "y": position.y()
            }
            asset.extras = extras_dict

    def save_model(self):
        """Save to file if filename set, else save as new file"""
        if self.model_file_name:
            self.add_positions_to_model()
            self.scene.model.save_to_file(self.model_file_name)
        else:
            self.save_as_model()

    def save_as_model(self):
        """ `Save as`. Let user select target file and save model."""
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
                self.scene.model.save_to_file(file_path)
            except Exception as e:
                print(f"Error saving model: {e}")
                self.show_error_popup("Error saving model: " + str(e))
                self.model_file_name = None
                return

    def save_as_drawio(self):
        """ `Save as`. Let user select target file and save .drawio file."""
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
            "DrawIO Files (*.drawio);;All Files (*)"
        )

        if not file_path:
            self.show_error_popup("No valid path detected for saving")
            return
        else:
            self.scene.model.name = Path(file_path).stem
            self.model_file_name = file_path
            try:
                create_drawio_file_with_images(
                    self.scene.model, output_filename=file_path
                )
            except Exception as e:
                print(f"Error saving model: {e}")
                self.show_error_popup("Error saving model: " + str(e))
                self.model_file_name = None
                return

    def save_as_scenario(self):
        """ `Save as`. Let user select target file and save scenario."""
        file_dialog = QFileDialog()
        file_dialog.setAcceptMode(QFileDialog.AcceptSave)
        file_dialog.setDefaultSuffix("yaml")
        file_path, _ = file_dialog.getSaveFileName()

        agents = self.scene.scenario.agent_settings if self.scene.scenario else {}
        # Add attacker agents from scene
        for attacker_item in self.scene.attacker_items:
            agent = agents.get(attacker_item.name)
            # Only thing that can be changed by GUI for agents is entry points
            if isinstance(agent, AttackerSettings):
                # If agent already exists in scenario, update entrypoints
                agent.entry_points = set(attacker_item.entry_points)
            else:
                # Otherwise, add new agent to scenario agents dict
                agents[attacker_item.name] = AttackerSettings(
                    name=attacker_item.name,
                    entry_points=set(attacker_item.entry_points),
                    type=AgentType.ATTACKER,
                    policy=RandomAgent,
                )
        if not file_path:
            print("No valid path detected for saving")
            return

        else:
            self.add_positions_to_model()
            # Create a new scenario based on settings in gui and save it to file
            # TODO: this is a hacky solution, instead malsim scenario should be easier to work with
            rewards = None
            false_negative_rates = None
            false_positive_rates = None
            is_actionable = None
            is_observable = None

            if self.scene.scenario:
                if self.scene.scenario.rewards:
                    rewards = (
                        self.scene.scenario.rewards.to_dict()
                    )
                if self.scene.scenario.false_negative_rates:
                    false_negative_rates = (
                        self.scene.scenario.false_negative_rates.to_dict()
                    )
                if self.scene.scenario.false_positive_rates:
                    false_positive_rates = (
                        self.scene.scenario.false_positive_rates.to_dict()
                    )
                if self.scene.scenario.is_actionable:
                    is_actionable = (
                        self.scene.scenario.is_actionable.to_dict()
                    )
                if self.scene.scenario.is_observable:
                    is_observable = (
                        self.scene.scenario.is_observable.to_dict()
                    )

            scenario = Scenario(
                lang_file=self.lang_file_path,
                model=self.scene.model,
                agent_settings=agents,
                rewards=rewards,
                false_negative_rates=false_negative_rates,
                false_positive_rates=false_positive_rates,
                actionable_steps=is_actionable,
                observable_steps=is_observable,
            )
            scenario.save_to_file(file_path)

    def quitApp(self):
        self.app.quit()

    def show_information_popup(self, message_text):
        """Show a popup with given message"""
        parent_widget = QWidget() #To maintain object lifetim
        message_box = QMessageBox(parent_widget)
        message_box.setIcon(QMessageBox.Information)
        message_box.setWindowTitle("Information")
        message_box.setText("This is default informative Text")
        message_box.setInformativeText(message_text)
        message_box.setStandardButtons(QMessageBox.Ok)
        message_box.exec()

    def show_error_popup(self, message_text):
        """Show error popup with given message"""
        parent_widget = QWidget() #To maintain object lifetim
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

        #Fill all the items from Scene one by one
        for child_asset_item in self.scene.items():
            if isinstance(child_asset_item,AssetItem):
                # Check if parent exists before adding child
                parent_item, parent_asset_type = self.object_explorer_tree\
                    .check_and_get_if_parent_asset_type_exists(
                        child_asset_item.asset_type
                    )

                if parent_asset_type:
                    self.object_explorer_tree.add_child_item(
                        parent_item,child_asset_item,
                        str(child_asset_item.asset_name)
                    )

    def on_theme_selection_change(self):
        """Set the selected theme"""
        selected_theme = self.theme_combo_box.currentText()
        print(f"{selected_theme} is the Theme selected")
        apply_stylesheet(self.app, theme=selected_theme)
