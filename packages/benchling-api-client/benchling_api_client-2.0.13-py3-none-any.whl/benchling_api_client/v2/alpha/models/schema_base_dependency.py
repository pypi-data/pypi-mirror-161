from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.base_manifest_config import BaseManifestConfig
from ..types import UNSET, Unset

T = TypeVar("T", bound="SchemaBaseDependency")


@attr.s(auto_attribs=True, repr=False)
class SchemaBaseDependency:
    """  """

    _name: str
    _field_definitions: Union[Unset, List[BaseManifestConfig]] = UNSET
    _description: Union[Unset, None, str] = UNSET
    _is_required: Union[Unset, bool] = False

    def __repr__(self):
        fields = []
        fields.append("name={}".format(repr(self._name)))
        fields.append("field_definitions={}".format(repr(self._field_definitions)))
        fields.append("description={}".format(repr(self._description)))
        fields.append("is_required={}".format(repr(self._is_required)))
        return "SchemaBaseDependency({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        name = self._name
        field_definitions: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._field_definitions, Unset):
            field_definitions = []
            for field_definitions_item_data in self._field_definitions:
                field_definitions_item = field_definitions_item_data.to_dict()

                field_definitions.append(field_definitions_item)

        description = self._description
        is_required = self._is_required

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "name": name,
            }
        )
        if field_definitions is not UNSET:
            field_dict["fieldDefinitions"] = field_definitions
        if description is not UNSET:
            field_dict["description"] = description
        if is_required is not UNSET:
            field_dict["isRequired"] = is_required

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_name() -> str:
            name = d.pop("name")
            return name

        name = get_name() if "name" in d else cast(str, UNSET)

        def get_field_definitions() -> Union[Unset, List[BaseManifestConfig]]:
            field_definitions = []
            _field_definitions = d.pop("fieldDefinitions")
            for field_definitions_item_data in _field_definitions or []:
                field_definitions_item = BaseManifestConfig.from_dict(field_definitions_item_data)

                field_definitions.append(field_definitions_item)

            return field_definitions

        field_definitions = (
            get_field_definitions()
            if "fieldDefinitions" in d
            else cast(Union[Unset, List[BaseManifestConfig]], UNSET)
        )

        def get_description() -> Union[Unset, None, str]:
            description = d.pop("description")
            return description

        description = get_description() if "description" in d else cast(Union[Unset, None, str], UNSET)

        def get_is_required() -> Union[Unset, bool]:
            is_required = d.pop("isRequired")
            return is_required

        is_required = get_is_required() if "isRequired" in d else cast(Union[Unset, bool], UNSET)

        schema_base_dependency = cls(
            name=name,
            field_definitions=field_definitions,
            description=description,
            is_required=is_required,
        )

        return schema_base_dependency

    @property
    def name(self) -> str:
        if isinstance(self._name, Unset):
            raise NotPresentError(self, "name")
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @property
    def field_definitions(self) -> List[BaseManifestConfig]:
        if isinstance(self._field_definitions, Unset):
            raise NotPresentError(self, "field_definitions")
        return self._field_definitions

    @field_definitions.setter
    def field_definitions(self, value: List[BaseManifestConfig]) -> None:
        self._field_definitions = value

    @field_definitions.deleter
    def field_definitions(self) -> None:
        self._field_definitions = UNSET

    @property
    def description(self) -> Optional[str]:
        if isinstance(self._description, Unset):
            raise NotPresentError(self, "description")
        return self._description

    @description.setter
    def description(self, value: Optional[str]) -> None:
        self._description = value

    @description.deleter
    def description(self) -> None:
        self._description = UNSET

    @property
    def is_required(self) -> bool:
        if isinstance(self._is_required, Unset):
            raise NotPresentError(self, "is_required")
        return self._is_required

    @is_required.setter
    def is_required(self, value: bool) -> None:
        self._is_required = value

    @is_required.deleter
    def is_required(self) -> None:
        self._is_required = UNSET
