from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class SearchDropdownUiBlockType(Enums.KnownString):
    SEARCH_DROPDOWN = "SEARCH_DROPDOWN"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "SearchDropdownUiBlockType":
        if not isinstance(val, str):
            raise ValueError(f"Value of SearchDropdownUiBlockType must be a string (encountered: {val})")
        newcls = Enum("SearchDropdownUiBlockType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(SearchDropdownUiBlockType, getattr(newcls, "_UNKNOWN"))
