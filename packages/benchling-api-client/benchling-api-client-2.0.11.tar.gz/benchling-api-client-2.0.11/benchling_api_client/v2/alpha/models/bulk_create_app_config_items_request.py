from typing import Any, cast, Dict, List, Optional, Type, TypeVar

import attr

from ..extensions import NotPresentError
from ..models.create_app_config_item import CreateAppConfigItem
from ..types import UNSET, Unset

T = TypeVar("T", bound="BulkCreateAppConfigItemsRequest")


@attr.s(auto_attribs=True, repr=False)
class BulkCreateAppConfigItemsRequest:
    """  """

    _app_configuration_items: List[CreateAppConfigItem]
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("app_configuration_items={}".format(repr(self._app_configuration_items)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "BulkCreateAppConfigItemsRequest({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        app_configuration_items = []
        for app_configuration_items_item_data in self._app_configuration_items:
            app_configuration_items_item = app_configuration_items_item_data.to_dict()

            app_configuration_items.append(app_configuration_items_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "appConfigurationItems": app_configuration_items,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_app_configuration_items() -> List[CreateAppConfigItem]:
            app_configuration_items = []
            _app_configuration_items = d.pop("appConfigurationItems")
            for app_configuration_items_item_data in _app_configuration_items:
                app_configuration_items_item = CreateAppConfigItem.from_dict(
                    app_configuration_items_item_data
                )

                app_configuration_items.append(app_configuration_items_item)

            return app_configuration_items

        app_configuration_items = (
            get_app_configuration_items()
            if "appConfigurationItems" in d
            else cast(List[CreateAppConfigItem], UNSET)
        )

        bulk_create_app_config_items_request = cls(
            app_configuration_items=app_configuration_items,
        )

        bulk_create_app_config_items_request.additional_properties = d
        return bulk_create_app_config_items_request

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties

    def get(self, key, default=None) -> Optional[Any]:
        return self.additional_properties.get(key, default)

    @property
    def app_configuration_items(self) -> List[CreateAppConfigItem]:
        if isinstance(self._app_configuration_items, Unset):
            raise NotPresentError(self, "app_configuration_items")
        return self._app_configuration_items

    @app_configuration_items.setter
    def app_configuration_items(self, value: List[CreateAppConfigItem]) -> None:
        self._app_configuration_items = value
