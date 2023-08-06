from typing import Any, cast, Dict, List, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="AppConfigItemsArchivalChange")


@attr.s(auto_attribs=True, repr=False)
class AppConfigItemsArchivalChange:
    """ IDs of all app config items that were archived or unarchived. """

    _item_ids: Union[Unset, List[str]] = UNSET

    def __repr__(self):
        fields = []
        fields.append("item_ids={}".format(repr(self._item_ids)))
        return "AppConfigItemsArchivalChange({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        item_ids: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._item_ids, Unset):
            item_ids = self._item_ids

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if item_ids is not UNSET:
            field_dict["itemIds"] = item_ids

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_item_ids() -> Union[Unset, List[str]]:
            item_ids = cast(List[str], d.pop("itemIds"))

            return item_ids

        item_ids = get_item_ids() if "itemIds" in d else cast(Union[Unset, List[str]], UNSET)

        app_config_items_archival_change = cls(
            item_ids=item_ids,
        )

        return app_config_items_archival_change

    @property
    def item_ids(self) -> List[str]:
        if isinstance(self._item_ids, Unset):
            raise NotPresentError(self, "item_ids")
        return self._item_ids

    @item_ids.setter
    def item_ids(self, value: List[str]) -> None:
        self._item_ids = value

    @item_ids.deleter
    def item_ids(self) -> None:
        self._item_ids = UNSET
