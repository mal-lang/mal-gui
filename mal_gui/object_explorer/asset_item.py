from __future__ import annotations
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt

from .item_base import ItemBase

if TYPE_CHECKING:
    from maltoolbox.model import ModelAsset

class AssetItem(ItemBase):
    # Starting Sequence Id with normal start at 100 (randomly taken)

    def __init__(
            self,
            asset: ModelAsset,
            image_path: str,
            parent=None,
        ):

        self.asset = asset
        self.asset_type = asset.lg_asset

        super().__init__(asset.lg_asset.name, image_path, parent)


    def update_name(self):
        super().update_name()
        self.asset.name = self.title

    def get_item_attribute_values(self):
        return {
            "Asset ID": self.asset.id,
            "Asset Name": self.asset.name,
            "Asset Type": self.asset_type
        }

    def serialize(self):
        return {
            'title': self.title,
            'image_path': self.image_path,
            'type': 'asset',
            'object': self.asset
        }
