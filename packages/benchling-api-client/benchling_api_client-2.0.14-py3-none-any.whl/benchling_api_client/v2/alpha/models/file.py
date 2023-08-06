from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.file_status_upload_status import FileStatusUploadStatus
from ..types import UNSET, Unset

T = TypeVar("T", bound="File")


@attr.s(auto_attribs=True, repr=False)
class File:
    """  """

    _id: Union[Unset, str] = UNSET
    _name: Union[Unset, str] = UNSET
    _error_message: Union[Unset, None, str] = UNSET
    _upload_status: Union[Unset, FileStatusUploadStatus] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("id={}".format(repr(self._id)))
        fields.append("name={}".format(repr(self._name)))
        fields.append("error_message={}".format(repr(self._error_message)))
        fields.append("upload_status={}".format(repr(self._upload_status)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "File({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        id = self._id
        name = self._name
        error_message = self._error_message
        upload_status: Union[Unset, int] = UNSET
        if not isinstance(self._upload_status, Unset):
            upload_status = self._upload_status.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name
        if error_message is not UNSET:
            field_dict["errorMessage"] = error_message
        if upload_status is not UNSET:
            field_dict["uploadStatus"] = upload_status

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_id() -> Union[Unset, str]:
            id = d.pop("id")
            return id

        id = get_id() if "id" in d else cast(Union[Unset, str], UNSET)

        def get_name() -> Union[Unset, str]:
            name = d.pop("name")
            return name

        name = get_name() if "name" in d else cast(Union[Unset, str], UNSET)

        def get_error_message() -> Union[Unset, None, str]:
            error_message = d.pop("errorMessage")
            return error_message

        error_message = get_error_message() if "errorMessage" in d else cast(Union[Unset, None, str], UNSET)

        def get_upload_status() -> Union[Unset, FileStatusUploadStatus]:
            upload_status = None
            _upload_status = d.pop("uploadStatus")
            if _upload_status is not None and _upload_status is not UNSET:
                try:
                    upload_status = FileStatusUploadStatus(_upload_status)
                except ValueError:
                    upload_status = FileStatusUploadStatus.of_unknown(_upload_status)

            return upload_status

        upload_status = (
            get_upload_status() if "uploadStatus" in d else cast(Union[Unset, FileStatusUploadStatus], UNSET)
        )

        file = cls(
            id=id,
            name=name,
            error_message=error_message,
            upload_status=upload_status,
        )

        file.additional_properties = d
        return file

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
    def error_message(self) -> Optional[str]:
        if isinstance(self._error_message, Unset):
            raise NotPresentError(self, "error_message")
        return self._error_message

    @error_message.setter
    def error_message(self, value: Optional[str]) -> None:
        self._error_message = value

    @error_message.deleter
    def error_message(self) -> None:
        self._error_message = UNSET

    @property
    def upload_status(self) -> FileStatusUploadStatus:
        if isinstance(self._upload_status, Unset):
            raise NotPresentError(self, "upload_status")
        return self._upload_status

    @upload_status.setter
    def upload_status(self, value: FileStatusUploadStatus) -> None:
        self._upload_status = value

    @upload_status.deleter
    def upload_status(self) -> None:
        self._upload_status = UNSET
