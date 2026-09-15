from types import SimpleNamespace

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog

from maltoolbox.language import LanguageGraphAsset, LanguageGraphAssociation
from maltoolbox.language.language_graph_assoc import (
    LanguageGraphAssociationField,
    link_association_to_assets,
)
from maltoolbox.model import ModelAsset

from mal_gui.connection_dialog import AssociationConnectionDialog


@pytest.fixture
def machine_execution_assets(app):
    machine = LanguageGraphAsset("Machine")
    infotainment = LanguageGraphAsset("InfotainmentSystem", own_super_asset=machine)
    application = LanguageGraphAsset("VehicularApplication")
    operating_system = LanguageGraphAsset(
        "OperatingSystem", own_super_asset=application
    )

    association = LanguageGraphAssociation(
        name="machineExecution",
        left_field=LanguageGraphAssociationField(machine, "hostMachine", 0, 1),
        right_field=LanguageGraphAssociationField(
            application, "machineExecutedApps", 0, 0
        ),
    )
    link_association_to_assets(association, machine, application)

    return {
        asset.name: ModelAsset(asset.name, asset_id, asset)
        for asset_id, asset in enumerate(
            (machine, infotainment, application, operating_system)
        )
    }


def make_dialog(start_asset, end_asset):
    start_item = SimpleNamespace(asset=start_asset, asset_type=start_asset.type)
    end_item = SimpleNamespace(asset=end_asset, asset_type=end_asset.type)
    return AssociationConnectionDialog(start_item, end_item, None, None)


@pytest.mark.parametrize(
    ("start_type", "end_type", "expected_fieldname"),
    [
        ("InfotainmentSystem", "OperatingSystem", "machineExecutedApps"),
        ("OperatingSystem", "InfotainmentSystem", "hostMachine"),
        ("Machine", "VehicularApplication", "machineExecutedApps"),
    ],
)
def test_inherited_endpoint_types_are_available(
    machine_execution_assets, start_type, end_type, expected_fieldname
):
    start_asset = machine_execution_assets[start_type]
    end_asset = machine_execution_assets[end_type]
    dialog = make_dialog(start_asset, end_asset)

    assert dialog.association_list_widget.count() == 1
    assert dialog.ok_button.isEnabled()
    selected_item = dialog.association_list_widget.currentItem()
    assert selected_item.data(Qt.UserRole)["fieldname"] == expected_fieldname

    dialog.ok_button_clicked()
    assert dialog.result() == QDialog.Accepted
    assert dialog.field_name == expected_fieldname

    start_asset.add_associated_assets(expected_fieldname, {end_asset})
    assert end_asset in start_asset.associated_assets[expected_fieldname]


def test_empty_selection_cannot_be_accepted(machine_execution_assets):
    unrelated_asset = ModelAsset("Unrelated", 4, LanguageGraphAsset("Unrelated"))
    dialog = make_dialog(machine_execution_assets["Machine"], unrelated_asset)

    assert dialog.association_list_widget.count() == 0
    assert not dialog.ok_button.isEnabled()

    dialog.ok_button_clicked()
    assert dialog.result() != QDialog.Accepted
    assert dialog.field_name is None
