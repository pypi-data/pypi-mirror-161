from typing import Any, Dict, Type, TypeVar

import attr

T = TypeVar("T", bound="InstanceProvider")


@attr.s(auto_attribs=True, repr=False)
class InstanceProvider:
    """  """

    def __repr__(self):
        fields = []
        return "InstanceProvider({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:

        field_dict: Dict[str, Any] = {}
        field_dict.update({})

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        src_dict.copy()
        instance_provider = cls()

        return instance_provider
