from __future__ import annotations
from typing import TYPE_CHECKING

from collections import namedtuple
from .asset_item import AssetItem
from .attacker_item import AttackerItem

if TYPE_CHECKING:
    from maltoolbox.model import ModelAsset, AttackerAttachment

AssetInfo = namedtuple(
    'AssetInfo', ['asset_type', 'asset_name', 'asset_image']
)


class AssetFactory():
    def __init__(self, parent=None):
        self.asset_registry: dict[str, list[AssetInfo]] = {}

    def add_key_value_to_asset_registry(self, key, value):
        if key not in self.asset_registry:
            self.asset_registry[key] = []

        if value not in self.asset_registry[key]:
            self.asset_registry[key].append(value)
            return True

        return False

    def register_asset(self, asset_name, image_path):
        self.add_key_value_to_asset_registry(
            asset_name,
            AssetInfo(asset_name, asset_name, image_path)
        )

    def get_asset_item(self, asset: ModelAsset):
        asset_type = asset.lg_asset.name
        asset_info: AssetInfo = self.asset_registry[asset_type][0]
        requested_item = AssetItem(asset, asset_info.asset_image)
        requested_item.build()
        return requested_item

    def get_attacker_item(self, attacker: AttackerAttachment):
        asset_info: AssetInfo = self.asset_registry['Attacker'][0]
        requested_item = AttackerItem(attacker, asset_info.asset_image)
        requested_item.build()
        return requested_item
