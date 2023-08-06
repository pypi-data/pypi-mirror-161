from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="BenchlingAppManifestSettings")


@attr.s(auto_attribs=True, repr=False)
class BenchlingAppManifestSettings:
    """  """

    _webhook_url: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("webhook_url={}".format(repr(self._webhook_url)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "BenchlingAppManifestSettings({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        webhook_url = self._webhook_url

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if webhook_url is not UNSET:
            field_dict["webhookUrl"] = webhook_url

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_webhook_url() -> Union[Unset, str]:
            webhook_url = d.pop("webhookUrl")
            return webhook_url

        webhook_url = get_webhook_url() if "webhookUrl" in d else cast(Union[Unset, str], UNSET)

        benchling_app_manifest_settings = cls(
            webhook_url=webhook_url,
        )

        benchling_app_manifest_settings.additional_properties = d
        return benchling_app_manifest_settings

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
    def webhook_url(self) -> str:
        """URL that Benchling sends app interaction payloads to. This destination should be backed by an endpoint owned by your application."""
        if isinstance(self._webhook_url, Unset):
            raise NotPresentError(self, "webhook_url")
        return self._webhook_url

    @webhook_url.setter
    def webhook_url(self, value: str) -> None:
        self._webhook_url = value

    @webhook_url.deleter
    def webhook_url(self) -> None:
        self._webhook_url = UNSET
