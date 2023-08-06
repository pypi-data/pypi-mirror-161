from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="AppConfigItemAppSummary")


@attr.s(auto_attribs=True, repr=False)
class AppConfigItemAppSummary:
    """  """

    _id: Union[Unset, str] = UNSET
    _version: Union[Unset, None, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("id={}".format(repr(self._id)))
        fields.append("version={}".format(repr(self._version)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "AppConfigItemAppSummary({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        id = self._id
        version = self._version

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if version is not UNSET:
            field_dict["version"] = version

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_id() -> Union[Unset, str]:
            id = d.pop("id")
            return id

        id = get_id() if "id" in d else cast(Union[Unset, str], UNSET)

        def get_version() -> Union[Unset, None, str]:
            version = d.pop("version")
            return version

        version = get_version() if "version" in d else cast(Union[Unset, None, str], UNSET)

        app_config_item_app_summary = cls(
            id=id,
            version=version,
        )

        app_config_item_app_summary.additional_properties = d
        return app_config_item_app_summary

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
    def id(self) -> str:
        """ The id of a Benchling app """
        if isinstance(self._id, Unset):
            raise NotPresentError(self, "id")
        return self._id

    @id.setter
    def id(self, value: str) -> None:
        self._id = value

    @id.deleter
    def id(self) -> None:
        self._id = UNSET

    @property
    def version(self) -> Optional[str]:
        """ The version of a Benchling app, if provided """
        if isinstance(self._version, Unset):
            raise NotPresentError(self, "version")
        return self._version

    @version.setter
    def version(self, value: Optional[str]) -> None:
        self._version = value

    @version.deleter
    def version(self) -> None:
        self._version = UNSET
