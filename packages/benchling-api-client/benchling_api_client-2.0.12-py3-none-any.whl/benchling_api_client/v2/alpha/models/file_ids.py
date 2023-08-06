from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="FileIds")


@attr.s(auto_attribs=True, repr=False)
class FileIds:
    """ Up to 25 files may be associated with a step data """

    _file_ids: Union[Unset, List[str]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("file_ids={}".format(repr(self._file_ids)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "FileIds({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        file_ids: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._file_ids, Unset):
            file_ids = self._file_ids

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if file_ids is not UNSET:
            field_dict["file_ids"] = file_ids

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_file_ids() -> Union[Unset, List[str]]:
            file_ids = cast(List[str], d.pop("file_ids"))

            return file_ids

        file_ids = get_file_ids() if "file_ids" in d else cast(Union[Unset, List[str]], UNSET)

        file_ids = cls(
            file_ids=file_ids,
        )

        file_ids.additional_properties = d
        return file_ids

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
    def file_ids(self) -> List[str]:
        if isinstance(self._file_ids, Unset):
            raise NotPresentError(self, "file_ids")
        return self._file_ids

    @file_ids.setter
    def file_ids(self, value: List[str]) -> None:
        self._file_ids = value

    @file_ids.deleter
    def file_ids(self) -> None:
        self._file_ids = UNSET
