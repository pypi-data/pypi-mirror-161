from typing import Any, Dict, Type, TypeVar

import attr

T = TypeVar("T", bound="BarcodeQueryValuePart")


@attr.s(auto_attribs=True, repr=False)
class BarcodeQueryValuePart:
    """  """

    def __repr__(self):
        fields = []
        return "BarcodeQueryValuePart({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:

        field_dict: Dict[str, Any] = {}
        field_dict.update({})

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        src_dict.copy()
        barcode_query_value_part = cls()

        return barcode_query_value_part
