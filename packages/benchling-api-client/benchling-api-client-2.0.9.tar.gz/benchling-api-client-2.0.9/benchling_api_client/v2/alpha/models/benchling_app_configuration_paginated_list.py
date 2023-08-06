from typing import Any, cast, Dict, List, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.app_config_item import AppConfigItem
from ..types import UNSET, Unset

T = TypeVar("T", bound="BenchlingAppConfigurationPaginatedList")


@attr.s(auto_attribs=True, repr=False)
class BenchlingAppConfigurationPaginatedList:
    """  """

    _configuration_items: Union[Unset, List[AppConfigItem]] = UNSET
    _next_token: Union[Unset, str] = UNSET

    def __repr__(self):
        fields = []
        fields.append("configuration_items={}".format(repr(self._configuration_items)))
        fields.append("next_token={}".format(repr(self._next_token)))
        return "BenchlingAppConfigurationPaginatedList({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        configuration_items: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._configuration_items, Unset):
            configuration_items = []
            for configuration_items_item_data in self._configuration_items:
                configuration_items_item = configuration_items_item_data.to_dict()

                configuration_items.append(configuration_items_item)

        next_token = self._next_token

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if configuration_items is not UNSET:
            field_dict["configurationItems"] = configuration_items
        if next_token is not UNSET:
            field_dict["nextToken"] = next_token

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_configuration_items() -> Union[Unset, List[AppConfigItem]]:
            configuration_items = []
            _configuration_items = d.pop("configurationItems")
            for configuration_items_item_data in _configuration_items or []:
                configuration_items_item = AppConfigItem.from_dict(configuration_items_item_data)

                configuration_items.append(configuration_items_item)

            return configuration_items

        configuration_items = (
            get_configuration_items()
            if "configurationItems" in d
            else cast(Union[Unset, List[AppConfigItem]], UNSET)
        )

        def get_next_token() -> Union[Unset, str]:
            next_token = d.pop("nextToken")
            return next_token

        next_token = get_next_token() if "nextToken" in d else cast(Union[Unset, str], UNSET)

        benchling_app_configuration_paginated_list = cls(
            configuration_items=configuration_items,
            next_token=next_token,
        )

        return benchling_app_configuration_paginated_list

    @property
    def configuration_items(self) -> List[AppConfigItem]:
        if isinstance(self._configuration_items, Unset):
            raise NotPresentError(self, "configuration_items")
        return self._configuration_items

    @configuration_items.setter
    def configuration_items(self, value: List[AppConfigItem]) -> None:
        self._configuration_items = value

    @configuration_items.deleter
    def configuration_items(self) -> None:
        self._configuration_items = UNSET

    @property
    def next_token(self) -> str:
        if isinstance(self._next_token, Unset):
            raise NotPresentError(self, "next_token")
        return self._next_token

    @next_token.setter
    def next_token(self, value: str) -> None:
        self._next_token = value

    @next_token.deleter
    def next_token(self) -> None:
        self._next_token = UNSET
