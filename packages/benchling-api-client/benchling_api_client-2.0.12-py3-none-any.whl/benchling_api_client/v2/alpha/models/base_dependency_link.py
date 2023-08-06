from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.app_config_item_app_summary import AppConfigItemAppSummary
from ..types import UNSET, Unset

T = TypeVar("T", bound="BaseDependencyLink")


@attr.s(auto_attribs=True, repr=False)
class BaseDependencyLink:
    """  """

    _app: Union[Unset, AppConfigItemAppSummary] = UNSET
    _app_id: Union[Unset, str] = UNSET
    _api_url: Union[Unset, str] = UNSET
    _id: Union[Unset, str] = UNSET
    _modified_at: Union[Unset, str] = UNSET
    _description: Union[Unset, None, str] = UNSET
    _is_required: Union[Unset, bool] = False
    _name: Union[Unset, str] = UNSET
    _resource_id: Union[Unset, None, str] = UNSET
    _resource_name: Union[Unset, None, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("app={}".format(repr(self._app)))
        fields.append("app_id={}".format(repr(self._app_id)))
        fields.append("api_url={}".format(repr(self._api_url)))
        fields.append("id={}".format(repr(self._id)))
        fields.append("modified_at={}".format(repr(self._modified_at)))
        fields.append("description={}".format(repr(self._description)))
        fields.append("is_required={}".format(repr(self._is_required)))
        fields.append("name={}".format(repr(self._name)))
        fields.append("resource_id={}".format(repr(self._resource_id)))
        fields.append("resource_name={}".format(repr(self._resource_name)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "BaseDependencyLink({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        app: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._app, Unset):
            app = self._app.to_dict()

        app_id = self._app_id
        api_url = self._api_url
        id = self._id
        modified_at = self._modified_at
        description = self._description
        is_required = self._is_required
        name = self._name
        resource_id = self._resource_id
        resource_name = self._resource_name

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if app is not UNSET:
            field_dict["app"] = app
        if app_id is not UNSET:
            field_dict["appId"] = app_id
        if api_url is not UNSET:
            field_dict["apiUrl"] = api_url
        if id is not UNSET:
            field_dict["id"] = id
        if modified_at is not UNSET:
            field_dict["modifiedAt"] = modified_at
        if description is not UNSET:
            field_dict["description"] = description
        if is_required is not UNSET:
            field_dict["isRequired"] = is_required
        if name is not UNSET:
            field_dict["name"] = name
        if resource_id is not UNSET:
            field_dict["resourceId"] = resource_id
        if resource_name is not UNSET:
            field_dict["resourceName"] = resource_name

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_app() -> Union[Unset, AppConfigItemAppSummary]:
            app: Union[Unset, AppConfigItemAppSummary] = UNSET
            _app = d.pop("app")
            if not isinstance(_app, Unset):
                app = AppConfigItemAppSummary.from_dict(_app)

            return app

        app = get_app() if "app" in d else cast(Union[Unset, AppConfigItemAppSummary], UNSET)

        def get_app_id() -> Union[Unset, str]:
            app_id = d.pop("appId")
            return app_id

        app_id = get_app_id() if "appId" in d else cast(Union[Unset, str], UNSET)

        def get_api_url() -> Union[Unset, str]:
            api_url = d.pop("apiUrl")
            return api_url

        api_url = get_api_url() if "apiUrl" in d else cast(Union[Unset, str], UNSET)

        def get_id() -> Union[Unset, str]:
            id = d.pop("id")
            return id

        id = get_id() if "id" in d else cast(Union[Unset, str], UNSET)

        def get_modified_at() -> Union[Unset, str]:
            modified_at = d.pop("modifiedAt")
            return modified_at

        modified_at = get_modified_at() if "modifiedAt" in d else cast(Union[Unset, str], UNSET)

        def get_description() -> Union[Unset, None, str]:
            description = d.pop("description")
            return description

        description = get_description() if "description" in d else cast(Union[Unset, None, str], UNSET)

        def get_is_required() -> Union[Unset, bool]:
            is_required = d.pop("isRequired")
            return is_required

        is_required = get_is_required() if "isRequired" in d else cast(Union[Unset, bool], UNSET)

        def get_name() -> Union[Unset, str]:
            name = d.pop("name")
            return name

        name = get_name() if "name" in d else cast(Union[Unset, str], UNSET)

        def get_resource_id() -> Union[Unset, None, str]:
            resource_id = d.pop("resourceId")
            return resource_id

        resource_id = get_resource_id() if "resourceId" in d else cast(Union[Unset, None, str], UNSET)

        def get_resource_name() -> Union[Unset, None, str]:
            resource_name = d.pop("resourceName")
            return resource_name

        resource_name = get_resource_name() if "resourceName" in d else cast(Union[Unset, None, str], UNSET)

        base_dependency_link = cls(
            app=app,
            app_id=app_id,
            api_url=api_url,
            id=id,
            modified_at=modified_at,
            description=description,
            is_required=is_required,
            name=name,
            resource_id=resource_id,
            resource_name=resource_name,
        )

        base_dependency_link.additional_properties = d
        return base_dependency_link

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
    def app(self) -> AppConfigItemAppSummary:
        if isinstance(self._app, Unset):
            raise NotPresentError(self, "app")
        return self._app

    @app.setter
    def app(self, value: AppConfigItemAppSummary) -> None:
        self._app = value

    @app.deleter
    def app(self) -> None:
        self._app = UNSET

    @property
    def app_id(self) -> str:
        """ The id of a Benchling app """
        if isinstance(self._app_id, Unset):
            raise NotPresentError(self, "app_id")
        return self._app_id

    @app_id.setter
    def app_id(self, value: str) -> None:
        self._app_id = value

    @app_id.deleter
    def app_id(self) -> None:
        self._app_id = UNSET

    @property
    def api_url(self) -> str:
        if isinstance(self._api_url, Unset):
            raise NotPresentError(self, "api_url")
        return self._api_url

    @api_url.setter
    def api_url(self, value: str) -> None:
        self._api_url = value

    @api_url.deleter
    def api_url(self) -> None:
        self._api_url = UNSET

    @property
    def id(self) -> str:
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
    def modified_at(self) -> str:
        """ DateTime the template was last modified """
        if isinstance(self._modified_at, Unset):
            raise NotPresentError(self, "modified_at")
        return self._modified_at

    @modified_at.setter
    def modified_at(self, value: str) -> None:
        self._modified_at = value

    @modified_at.deleter
    def modified_at(self) -> None:
        self._modified_at = UNSET

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

    @property
    def name(self) -> str:
        if isinstance(self._name, Unset):
            raise NotPresentError(self, "name")
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @name.deleter
    def name(self) -> None:
        self._name = UNSET

    @property
    def resource_id(self) -> Optional[str]:
        if isinstance(self._resource_id, Unset):
            raise NotPresentError(self, "resource_id")
        return self._resource_id

    @resource_id.setter
    def resource_id(self, value: Optional[str]) -> None:
        self._resource_id = value

    @resource_id.deleter
    def resource_id(self) -> None:
        self._resource_id = UNSET

    @property
    def resource_name(self) -> Optional[str]:
        if isinstance(self._resource_name, Unset):
            raise NotPresentError(self, "resource_name")
        return self._resource_name

    @resource_name.setter
    def resource_name(self, value: Optional[str]) -> None:
        self._resource_name = value

    @resource_name.deleter
    def resource_name(self) -> None:
        self._resource_name = UNSET
