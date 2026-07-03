from __future__ import annotations
from typing import TYPE_CHECKING

from PySide6.QtGui import QUndoCommand

if TYPE_CHECKING:
    from ..model_scene import ModelScene
    from ..object_explorer import MetaDetectorItem, AssetItem


class CreateMetaDetectorConnectionCommand(QUndoCommand):
    def __init__(
        self,
        scene: ModelScene,
        meta_detector_item: MetaDetectorItem,
        asset_item: AssetItem,
        parent=None,
    ):
        super().__init__(parent)
        self.scene = scene
        self.meta_detector_item = meta_detector_item
        self.asset_item = asset_item
        self.connection = None
        self.asset_name = self.asset_item.asset.name
        self.label_value = self.meta_detector_item.connected_asset_labels.get(
            self.asset_name, 1
        )

    def _add_asset(self):
        if self.asset_name not in self.meta_detector_item.connected_assets:
            self.meta_detector_item.connected_assets.append(self.asset_name)
        self.meta_detector_item.connected_asset_labels[self.asset_name] = (
            self.label_value
        )

    def _remove_asset(self):
        try:
            self.meta_detector_item.connected_assets.remove(self.asset_name)
        except ValueError:
            pass
        self.meta_detector_item.connected_asset_labels.pop(self.asset_name, None)

    def redo(self):
        self.connection = self.scene.add_meta_detector_connection(
            self.meta_detector_item, self.asset_item, self.label_value
        )
        self._add_asset()

    def undo(self):
        if self.connection:
            self.connection.delete()
        self._remove_asset()
