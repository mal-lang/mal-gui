from __future__ import annotations
from typing import TYPE_CHECKING
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSizePolicy,
)

if TYPE_CHECKING:
    from .object_explorer import AssetItem, AttackerItem
    from maltoolbox.language import LanguageGraph, LanguageGraphAsset
    from maltoolbox.model import Model, ModelAsset

class ConnectionDialog(QDialog):
    def filter_items(self, text):
        pass

    def ok_button_clicked(self):
        pass


class AssociationConnectionDialog(ConnectionDialog):
    def __init__(
            self,
            start_item: AssetItem,
            end_item: AssetItem,
            lang_graph: LanguageGraph,
            model: Model,
            parent=None
        ):
        super().__init__(parent)

        self.lang_graph: LanguageGraph = lang_graph
        self.model = model

        self.setWindowTitle("Select Association Type")
        self.setMinimumWidth(300)

        print(f'START ITEM TYPE {start_item.asset_type}')
        print(f'END ITEM TYPE {end_item.asset_type}')

        self.association_list_widget = QListWidget()

        self.start_asset: ModelAsset = start_item.asset
        self.end_asset: ModelAsset = end_item.asset
        self.field_name = None

        self.layout = QVBoxLayout()
        self.label = (
            QLabel(f"{self.start_asset.name} -> {self.end_asset.name}")
        )
        self.layout.addWidget(self.label)
        self.filter_edit = QLineEdit()
        self.filter_edit.setPlaceholderText("Type to filter...")
        self.filter_edit.textChanged.connect(self.filter_items)
        self.layout.addWidget(self.filter_edit)

        possible_assocs = self.start_asset.lg_asset.associations
        for fieldname, association in possible_assocs.items():
            field = association.get_field(fieldname)

            # If assoc ends with end_assets type, give that assoc
            # as option in list widget
            if field.asset == self.end_asset.lg_asset:
                assoc_list_item = QListWidgetItem(self.start_asset.name + "." + fieldname + " = " + self.end_asset.name)
                assoc_list_item.setData(
                    Qt.UserRole,
                    {
                        'from': self.start_asset,
                        'to': self.end_asset,
                        'fieldname': fieldname
                    }
                )
                self.association_list_widget.addItem(assoc_list_item)

        self.layout.addWidget(self.association_list_widget)

        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.ok_button_clicked)
        self.ok_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        button_layout.addWidget(self.ok_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        self.cancel_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        button_layout.addWidget(self.cancel_button)

        self.layout.addLayout(button_layout)

        self.setLayout(self.layout)

        # Select the first item by default
        self.association_list_widget.setCurrentRow(0)

    def filter_items(self, text):
        for i in range(self.association_list_widget.count()):
            item = self.association_list_widget.item(i)
            item.setHidden(text.lower() not in item.text().lower())

    def ok_button_clicked(self):
        selected_item = self.association_list_widget.currentItem()

        if selected_item:
            data = selected_item.data(Qt.UserRole)

            from_asset: ModelAsset = data.get('from')
            to_asset: ModelAsset = data.get('to')
            self.field_name: str = data.get('fieldname')

            print(f'{from_asset}.{self.field_name} = {to_asset} chosen')


        self.accept()

class EntrypointConnectionDialog(ConnectionDialog):
    def __init__(
            self,
            attacker_item: AttackerItem,
            asset_item: AssetItem,
            lang_graph: LanguageGraph,
            model,
            parent=None
        ):
        super().__init__(parent)

        self.lang_graph = lang_graph
        self.model = model

        self.setWindowTitle("Select Entry Point")
        self.setMinimumWidth(300)

        self.attack_step_list_widget = QListWidget()
        attacker = attacker_item.attacker

        if asset_item.asset is not None:
            asset_type = self.lang_graph.assets[asset_item.asset.type]

            # Find asset attack steps already part of attacker entry points
            entry_point_tuple = attacker.get_entry_point_tuple(
                asset_item.asset
            )

            if entry_point_tuple is not None:
                entry_point_attack_steps = entry_point_tuple[1]
            else:
                entry_point_attack_steps = []

            for attack_step in asset_type.attack_steps.values():
                if attack_step.type not in ['or', 'and']:
                    continue

                if attack_step.name not in entry_point_attack_steps:
                    print(attack_step.name)
                    item = QListWidgetItem(attack_step.name)
                    self.attack_step_list_widget.addItem(item)

            self.layout = QVBoxLayout()

            self.label = QLabel(
                f"{attacker.name}:{asset_item.asset.name}")
            self.layout.addWidget(self.label)

            self.filter_edit = QLineEdit()
            self.filter_edit.setPlaceholderText("Type to filter...")
            self.filter_edit.textChanged.connect(self.filter_items)
            self.layout.addWidget(self.filter_edit)
            self.layout.addWidget(self.attack_step_list_widget)

        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.ok_button_clicked)
        self.ok_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        button_layout.addWidget(self.ok_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        self.cancel_button.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Fixed)
        button_layout.addWidget(self.cancel_button)

        self.layout.addLayout(button_layout)
        self.setLayout(self.layout)

        # Select the first item by default
        self.attack_step_list_widget.setCurrentRow(0)

    def filter_items(self, text):
        for i in range(self.attack_step_list_widget.count()):
            item = self.attack_step_list_widget.item(i)
            item.setHidden(text.lower() not in item.text().lower())

    def ok_button_clicked(self):
        self.accept()
