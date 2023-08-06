from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.base_manifest_config import BaseManifestConfig
from ..models.dropdown_dependency_types import DropdownDependencyTypes
from ..types import UNSET, Unset

T = TypeVar("T", bound="DropdownDependency")


@attr.s(auto_attribs=True, repr=False)
class DropdownDependency:
    """  """

    _type: DropdownDependencyTypes
    _name: str
    _options: Union[Unset, List[BaseManifestConfig]] = UNSET
    _description: Union[Unset, None, str] = UNSET
    _is_required: Union[Unset, bool] = False

    def __repr__(self):
        fields = []
        fields.append("type={}".format(repr(self._type)))
        fields.append("name={}".format(repr(self._name)))
        fields.append("options={}".format(repr(self._options)))
        fields.append("description={}".format(repr(self._description)))
        fields.append("is_required={}".format(repr(self._is_required)))
        return "DropdownDependency({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        type = self._type.value

        name = self._name
        options: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._options, Unset):
            options = []
            for options_item_data in self._options:
                options_item = options_item_data.to_dict()

                options.append(options_item)

        description = self._description
        is_required = self._is_required

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "type": type,
                "name": name,
            }
        )
        if options is not UNSET:
            field_dict["options"] = options
        if description is not UNSET:
            field_dict["description"] = description
        if is_required is not UNSET:
            field_dict["isRequired"] = is_required

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_type() -> DropdownDependencyTypes:
            _type = d.pop("type")
            try:
                type = DropdownDependencyTypes(_type)
            except ValueError:
                type = DropdownDependencyTypes.of_unknown(_type)

            return type

        type = get_type() if "type" in d else cast(DropdownDependencyTypes, UNSET)

        def get_name() -> str:
            name = d.pop("name")
            return name

        name = get_name() if "name" in d else cast(str, UNSET)

        def get_options() -> Union[Unset, List[BaseManifestConfig]]:
            options = []
            _options = d.pop("options")
            for options_item_data in _options or []:
                options_item = BaseManifestConfig.from_dict(options_item_data)

                options.append(options_item)

            return options

        options = get_options() if "options" in d else cast(Union[Unset, List[BaseManifestConfig]], UNSET)

        def get_description() -> Union[Unset, None, str]:
            description = d.pop("description")
            return description

        description = get_description() if "description" in d else cast(Union[Unset, None, str], UNSET)

        def get_is_required() -> Union[Unset, bool]:
            is_required = d.pop("isRequired")
            return is_required

        is_required = get_is_required() if "isRequired" in d else cast(Union[Unset, bool], UNSET)

        dropdown_dependency = cls(
            type=type,
            name=name,
            options=options,
            description=description,
            is_required=is_required,
        )

        return dropdown_dependency

    @property
    def type(self) -> DropdownDependencyTypes:
        if isinstance(self._type, Unset):
            raise NotPresentError(self, "type")
        return self._type

    @type.setter
    def type(self, value: DropdownDependencyTypes) -> None:
        self._type = value

    @property
    def name(self) -> str:
        if isinstance(self._name, Unset):
            raise NotPresentError(self, "name")
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @property
    def options(self) -> List[BaseManifestConfig]:
        if isinstance(self._options, Unset):
            raise NotPresentError(self, "options")
        return self._options

    @options.setter
    def options(self, value: List[BaseManifestConfig]) -> None:
        self._options = value

    @options.deleter
    def options(self) -> None:
        self._options = UNSET

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
