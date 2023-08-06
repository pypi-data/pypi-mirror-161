from typing import Any, cast, Dict, List, Optional, Type, TypeVar

import attr

from ..extensions import NotPresentError
from ..models.chip_ui_block_type import ChipUiBlockType
from ..types import UNSET, Unset

T = TypeVar("T", bound="ChipUiBlock")


@attr.s(auto_attribs=True, repr=False)
class ChipUiBlock:
    """  """

    _type: ChipUiBlockType
    _value: str
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("type={}".format(repr(self._type)))
        fields.append("value={}".format(repr(self._value)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "ChipUiBlock({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        type = self._type.value

        value = self._value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type,
                "value": value,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_type() -> ChipUiBlockType:
            _type = d.pop("type")
            try:
                type = ChipUiBlockType(_type)
            except ValueError:
                type = ChipUiBlockType.of_unknown(_type)

            return type

        type = get_type() if "type" in d else cast(ChipUiBlockType, UNSET)

        def get_value() -> str:
            value = d.pop("value")
            return value

        value = get_value() if "value" in d else cast(str, UNSET)

        chip_ui_block = cls(
            type=type,
            value=value,
        )

        chip_ui_block.additional_properties = d
        return chip_ui_block

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
    def type(self) -> ChipUiBlockType:
        if isinstance(self._type, Unset):
            raise NotPresentError(self, "type")
        return self._type

    @type.setter
    def type(self, value: ChipUiBlockType) -> None:
        self._type = value

    @property
    def value(self) -> str:
        if isinstance(self._value, Unset):
            raise NotPresentError(self, "value")
        return self._value

    @value.setter
    def value(self, value: str) -> None:
        self._value = value
