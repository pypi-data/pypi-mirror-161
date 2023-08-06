from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.form_raw_string_query_value_part_type import FormRawStringQueryValuePartType
from ..types import UNSET, Unset

T = TypeVar("T", bound="FormRawStringQueryValuePart")


@attr.s(auto_attribs=True, repr=False)
class FormRawStringQueryValuePart:
    """  """

    _type: Union[Unset, FormRawStringQueryValuePartType] = UNSET
    _value: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("type={}".format(repr(self._type)))
        fields.append("value={}".format(repr(self._value)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "FormRawStringQueryValuePart({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        type: Union[Unset, int] = UNSET
        if not isinstance(self._type, Unset):
            type = self._type.value

        value = self._value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if type is not UNSET:
            field_dict["type"] = type
        if value is not UNSET:
            field_dict["value"] = value

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_type() -> Union[Unset, FormRawStringQueryValuePartType]:
            type = None
            _type = d.pop("type")
            if _type is not None and _type is not UNSET:
                try:
                    type = FormRawStringQueryValuePartType(_type)
                except ValueError:
                    type = FormRawStringQueryValuePartType.of_unknown(_type)

            return type

        type = get_type() if "type" in d else cast(Union[Unset, FormRawStringQueryValuePartType], UNSET)

        def get_value() -> Union[Unset, str]:
            value = d.pop("value")
            return value

        value = get_value() if "value" in d else cast(Union[Unset, str], UNSET)

        form_raw_string_query_value_part = cls(
            type=type,
            value=value,
        )

        form_raw_string_query_value_part.additional_properties = d
        return form_raw_string_query_value_part

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
    def type(self) -> FormRawStringQueryValuePartType:
        if isinstance(self._type, Unset):
            raise NotPresentError(self, "type")
        return self._type

    @type.setter
    def type(self, value: FormRawStringQueryValuePartType) -> None:
        self._type = value

    @type.deleter
    def type(self) -> None:
        self._type = UNSET

    @property
    def value(self) -> str:
        if isinstance(self._value, Unset):
            raise NotPresentError(self, "value")
        return self._value

    @value.setter
    def value(self, value: str) -> None:
        self._value = value

    @value.deleter
    def value(self) -> None:
        self._value = UNSET
