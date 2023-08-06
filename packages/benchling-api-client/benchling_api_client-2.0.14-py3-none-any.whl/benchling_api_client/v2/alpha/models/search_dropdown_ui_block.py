from typing import Any, cast, Dict, List, Optional, Type, TypeVar

import attr

from ..extensions import NotPresentError
from ..models.search_dropdown_ui_block_item_type import SearchDropdownUiBlockItemType
from ..models.search_dropdown_ui_block_type import SearchDropdownUiBlockType
from ..types import UNSET, Unset

T = TypeVar("T", bound="SearchDropdownUiBlock")


@attr.s(auto_attribs=True, repr=False)
class SearchDropdownUiBlock:
    """  """

    _item_type: SearchDropdownUiBlockItemType
    _type: SearchDropdownUiBlockType
    _value: Optional[str]
    _schema_id: Optional[str]
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("item_type={}".format(repr(self._item_type)))
        fields.append("type={}".format(repr(self._type)))
        fields.append("value={}".format(repr(self._value)))
        fields.append("schema_id={}".format(repr(self._schema_id)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "SearchDropdownUiBlock({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        item_type = self._item_type.value

        type = self._type.value

        value = self._value
        schema_id = self._schema_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "itemType": item_type,
                "type": type,
                "value": value,
                "schemaId": schema_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_item_type() -> SearchDropdownUiBlockItemType:
            _item_type = d.pop("itemType")
            try:
                item_type = SearchDropdownUiBlockItemType(_item_type)
            except ValueError:
                item_type = SearchDropdownUiBlockItemType.of_unknown(_item_type)

            return item_type

        item_type = get_item_type() if "itemType" in d else cast(SearchDropdownUiBlockItemType, UNSET)

        def get_type() -> SearchDropdownUiBlockType:
            _type = d.pop("type")
            try:
                type = SearchDropdownUiBlockType(_type)
            except ValueError:
                type = SearchDropdownUiBlockType.of_unknown(_type)

            return type

        type = get_type() if "type" in d else cast(SearchDropdownUiBlockType, UNSET)

        def get_value() -> Optional[str]:
            value = d.pop("value")
            return value

        value = get_value() if "value" in d else cast(Optional[str], UNSET)

        def get_schema_id() -> Optional[str]:
            schema_id = d.pop("schemaId")
            return schema_id

        schema_id = get_schema_id() if "schemaId" in d else cast(Optional[str], UNSET)

        search_dropdown_ui_block = cls(
            item_type=item_type,
            type=type,
            value=value,
            schema_id=schema_id,
        )

        search_dropdown_ui_block.additional_properties = d
        return search_dropdown_ui_block

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
    def item_type(self) -> SearchDropdownUiBlockItemType:
        if isinstance(self._item_type, Unset):
            raise NotPresentError(self, "item_type")
        return self._item_type

    @item_type.setter
    def item_type(self, value: SearchDropdownUiBlockItemType) -> None:
        self._item_type = value

    @property
    def type(self) -> SearchDropdownUiBlockType:
        if isinstance(self._type, Unset):
            raise NotPresentError(self, "type")
        return self._type

    @type.setter
    def type(self, value: SearchDropdownUiBlockType) -> None:
        self._type = value

    @property
    def value(self) -> Optional[str]:
        if isinstance(self._value, Unset):
            raise NotPresentError(self, "value")
        return self._value

    @value.setter
    def value(self, value: Optional[str]) -> None:
        self._value = value

    @property
    def schema_id(self) -> Optional[str]:
        if isinstance(self._schema_id, Unset):
            raise NotPresentError(self, "schema_id")
        return self._schema_id

    @schema_id.setter
    def schema_id(self, value: Optional[str]) -> None:
        self._schema_id = value
