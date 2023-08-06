from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="AnalysisDatasetIds")


@attr.s(auto_attribs=True, repr=False)
class AnalysisDatasetIds:
    """  """

    _dataset_ids: Union[Unset, List[str]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("dataset_ids={}".format(repr(self._dataset_ids)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "AnalysisDatasetIds({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        dataset_ids: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._dataset_ids, Unset):
            dataset_ids = self._dataset_ids

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if dataset_ids is not UNSET:
            field_dict["dataset_ids"] = dataset_ids

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_dataset_ids() -> Union[Unset, List[str]]:
            dataset_ids = cast(List[str], d.pop("dataset_ids"))

            return dataset_ids

        dataset_ids = get_dataset_ids() if "dataset_ids" in d else cast(Union[Unset, List[str]], UNSET)

        analysis_dataset_ids = cls(
            dataset_ids=dataset_ids,
        )

        analysis_dataset_ids.additional_properties = d
        return analysis_dataset_ids

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
    def dataset_ids(self) -> List[str]:
        if isinstance(self._dataset_ids, Unset):
            raise NotPresentError(self, "dataset_ids")
        return self._dataset_ids

    @dataset_ids.setter
    def dataset_ids(self, value: List[str]) -> None:
        self._dataset_ids = value

    @dataset_ids.deleter
    def dataset_ids(self) -> None:
        self._dataset_ids = UNSET
