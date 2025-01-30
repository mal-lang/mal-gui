from __future__ import annotations
from typing import TYPE_CHECKING
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
    from .object_explorer.asset_base import AssetBase
    from maltoolbox.language import LanguageClassesFactory
class ConnectionDialog(QDialog):
    def filter_items(self, text):
        pass

    def ok_button_clicked(self):
        pass


class AssociationConnectionDialog(ConnectionDialog):
    def __init__(
            self,
            start_item: AssetBase,
            end_item: AssetBase,
            lang_graph,
            lcs: LanguageClassesFactory,
            model,
            parent=None
        ):
        super().__init__(parent)

        self.lang_graph = lang_graph
        self.lcs = lcs
        self.model = model

        self.setWindowTitle("Select Association Type")
        self.setMinimumWidth(300)

        print(f'START ITEM TYPE {start_item.asset_type}')
        print(f'END ITEM TYPE {end_item.asset_type}')

        self.association_list_widget = QListWidget()

        start_asset = start_item.asset
        end_asset = end_item.asset
        self.start_asset_type = start_asset.type
        self.end_asset_type = end_asset.type
        self.start_asset_name = start_asset.name
        self.end_asset_name = end_asset.name
        self.layout = QVBoxLayout()
        self.label = \
            QLabel(f"{self.start_asset_name} : {self.end_asset_name}")
        self.layout.addWidget(self.label)
        self.filter_edit = QLineEdit()
        self.filter_edit.setPlaceholderText("Type to filter...")
        self.filter_edit.textChanged.connect(self.filter_items)
        self.layout.addWidget(self.filter_edit)

        # Get asset type from lang graph
        start_asset_type = self.lang_graph.assets.get(start_asset.type)
        if start_asset_type is None:
            raise LookupError(f'Failed to find asset "{start_asset.type}" '
                'in language graph.')

        end_asset_type = self.lang_graph.assets.get(end_asset.type)
        if end_asset_type is None:
            raise LookupError(f'Failed to find asset "{end_asset.type}" '
                'in language graph.')

        self._str_to_assoc = {}
        for assoc in start_asset_type.associations.values():
            asset_pairs = []
            opposite_asset = assoc.get_opposite_asset(start_asset_type)
            # Check if the other side of the association matches the other end
            # and if the exact association does not already exist in the
            # model.
            if end_asset_type.is_subasset_of(opposite_asset):
                print("IDENTIFIED MATCH  ++++++++++++")
                if start_asset_type.is_subasset_of(assoc.left_field.asset):
                    asset_pairs.append((start_asset, end_asset))
                else:
                    asset_pairs.append((end_asset, start_asset))
            if start_asset_type.is_subasset_of(opposite_asset):
                # The association could be applied either way, add the
                # reverse association as well.
                other_asset = assoc.get_opposite_asset(opposite_asset)
                # Check if the other side of the association matches the other end
                # and if the exact association does not already exist in the
                # model.
                if end_asset_type.is_subasset_of(other_asset):
                    print("REVERSE ASSOC  ++++++++++++")
                    # We need to create the reverse association as well
                    asset_pairs.append((end_asset, start_asset))
            for (left_asset, right_asset) in asset_pairs:
                if not self.model.association_exists_between_assets(
                        assoc.name,
                        left_asset,
                        right_asset):
                    formatted_assoc_str = left_asset.name + "." + \
                        assoc.left_field.fieldname + "-->" + \
                        assoc.name + "-->" + \
                        right_asset.name + "." + \
                        assoc.right_field.fieldname
                    self._str_to_assoc[formatted_assoc_str] = (
                        assoc,
                        left_asset,
                        right_asset
                    )
                    self.association_list_widget.addItem(QListWidgetItem(formatted_assoc_str))
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
            selected_association_text = selected_item.text()

            (assoc, left_asset, right_asset) = \
                self._str_to_assoc[selected_association_text]

            # TODO: Create association based on its full name instead in order
            # to avoid conflicts when multiple associations with the same name
            # exist.

            assoc_type_class = self.lcs.get_association_class(assoc.full_name)
            association = assoc_type_class()

            print(
                f'N:{assoc.name} LF:{assoc.left_field.fieldname} '
                f'LA:{left_asset.name} RF:{assoc.right_field.fieldname} '
                f'RA:{right_asset.name}'
            )
            setattr(association, assoc.left_field.fieldname, [left_asset])
            setattr(association, assoc.right_field.fieldname, [right_asset])
            selected_item.association = association
            # self.model.add_association(association)
        self.accept()

class EntrypointConnectionDialog(ConnectionDialog):
    def __init__(
            self,
            attacker_item,
            asset_item,
            lang_graph,
            lcs,
            model,
            parent=None
        ):
        super().__init__(parent)

        self.lang_graph = lang_graph
        self.lcs = lcs
        self.model = model

        self.setWindowTitle("Select Entry Point")
        self.setMinimumWidth(300)

        print(f'Attacker ITEM TYPE {attacker_item.asset_type}')
        print(f'Asset ITEM TYPE {asset_item.asset_type}')

        self.attack_step_list_widget = QListWidget()
        attacker = attacker_item.attackerAttachment

        if asset_item.asset is not None:
            asset_type = \
                self.lang_graph.get_asset_by_name(asset_item.asset.type)

            # Find asset attack steps already part of attacker entry points
            entry_point_tuple = attacker.get_entry_point_tuple(
                asset_item.asset)
            if entry_point_tuple is not None:
                entry_point_attack_steps = entry_point_tuple[1]
            else:
                entry_point_attack_steps = []

            for attack_step in asset_type.attack_steps:
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
