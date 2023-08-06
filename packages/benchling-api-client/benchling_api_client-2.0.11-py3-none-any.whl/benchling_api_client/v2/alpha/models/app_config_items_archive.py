from typing import Any, cast, Dict, List, Type, TypeVar

import attr

from ..extensions import NotPresentError
from ..models.app_config_items_archive_reason import AppConfigItemsArchiveReason
from ..types import UNSET, Unset

T = TypeVar("T", bound="AppConfigItemsArchive")


@attr.s(auto_attribs=True, repr=False)
class AppConfigItemsArchive:
    """  """

    _item_ids: List[str]
    _reason: AppConfigItemsArchiveReason

    def __repr__(self):
        fields = []
        fields.append("item_ids={}".format(repr(self._item_ids)))
        fields.append("reason={}".format(repr(self._reason)))
        return "AppConfigItemsArchive({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        item_ids = self._item_ids

        reason = self._reason.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "itemIds": item_ids,
                "reason": reason,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_item_ids() -> List[str]:
            item_ids = cast(List[str], d.pop("itemIds"))

            return item_ids

        item_ids = get_item_ids() if "itemIds" in d else cast(List[str], UNSET)

        def get_reason() -> AppConfigItemsArchiveReason:
            _reason = d.pop("reason")
            try:
                reason = AppConfigItemsArchiveReason(_reason)
            except ValueError:
                reason = AppConfigItemsArchiveReason.of_unknown(_reason)

            return reason

        reason = get_reason() if "reason" in d else cast(AppConfigItemsArchiveReason, UNSET)

        app_config_items_archive = cls(
            item_ids=item_ids,
            reason=reason,
        )

        return app_config_items_archive

    @property
    def item_ids(self) -> List[str]:
        """ Array of app configuration item IDs """
        if isinstance(self._item_ids, Unset):
            raise NotPresentError(self, "item_ids")
        return self._item_ids

    @item_ids.setter
    def item_ids(self, value: List[str]) -> None:
        self._item_ids = value

    @property
    def reason(self) -> AppConfigItemsArchiveReason:
        """ Reason that app configuration items are being archived. Actual reason enum varies by tenant. """
        if isinstance(self._reason, Unset):
            raise NotPresentError(self, "reason")
        return self._reason

    @reason.setter
    def reason(self, value: AppConfigItemsArchiveReason) -> None:
        self._reason = value
