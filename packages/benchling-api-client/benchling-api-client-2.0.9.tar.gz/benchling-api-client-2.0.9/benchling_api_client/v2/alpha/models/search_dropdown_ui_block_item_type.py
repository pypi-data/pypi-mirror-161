from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class SearchDropdownUiBlockItemType(Enums.KnownString):
    DNA_SEQUENCE = "dna_sequence"
    DNA_OLIGO = "dna_oligo"
    AA_SEQUENCE = "aa_sequence"
    CUSTOM_ENTITY = "custom_entity"
    MIXTURE = "mixture"
    BOX = "box"
    CONTAINER = "container"
    LOCATION = "location"
    PLATE = "plate"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "SearchDropdownUiBlockItemType":
        if not isinstance(val, str):
            raise ValueError(f"Value of SearchDropdownUiBlockItemType must be a string (encountered: {val})")
        newcls = Enum("SearchDropdownUiBlockItemType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(SearchDropdownUiBlockItemType, getattr(newcls, "_UNKNOWN"))
