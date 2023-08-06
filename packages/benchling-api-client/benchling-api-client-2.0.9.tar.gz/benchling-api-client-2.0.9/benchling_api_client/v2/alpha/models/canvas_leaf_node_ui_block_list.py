from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError, UnknownType
from ..models.button_ui_block import ButtonUiBlock
from ..models.chip_ui_block import ChipUiBlock
from ..models.markdown_ui_block import MarkdownUiBlock
from ..models.search_dropdown_ui_block import SearchDropdownUiBlock
from ..models.text_input_ui_block import TextInputUiBlock
from ..models.text_label_ui_block import TextLabelUiBlock
from ..types import UNSET, Unset

T = TypeVar("T", bound="CanvasLeafNodeUiBlockList")


@attr.s(auto_attribs=True, repr=False)
class CanvasLeafNodeUiBlockList:
    """  """

    _children: List[
        Union[
            TextLabelUiBlock,
            TextInputUiBlock,
            ButtonUiBlock,
            MarkdownUiBlock,
            ChipUiBlock,
            SearchDropdownUiBlock,
            UnknownType,
        ]
    ]
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("children={}".format(repr(self._children)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "CanvasLeafNodeUiBlockList({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        children = []
        for children_item_data in self._children:
            if isinstance(children_item_data, UnknownType):
                children_item = children_item_data.value
            elif isinstance(children_item_data, TextLabelUiBlock):
                children_item = children_item_data.to_dict()

            elif isinstance(children_item_data, TextInputUiBlock):
                children_item = children_item_data.to_dict()

            elif isinstance(children_item_data, ButtonUiBlock):
                children_item = children_item_data.to_dict()

            elif isinstance(children_item_data, MarkdownUiBlock):
                children_item = children_item_data.to_dict()

            elif isinstance(children_item_data, ChipUiBlock):
                children_item = children_item_data.to_dict()

            else:
                children_item = children_item_data.to_dict()

            children.append(children_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "children": children,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_children() -> List[
            Union[
                TextLabelUiBlock,
                TextInputUiBlock,
                ButtonUiBlock,
                MarkdownUiBlock,
                ChipUiBlock,
                SearchDropdownUiBlock,
                UnknownType,
            ]
        ]:
            children = []
            _children = d.pop("children")
            for children_item_data in _children:

                def _parse_children_item(
                    data: Union[Dict[str, Any]]
                ) -> Union[
                    TextLabelUiBlock,
                    TextInputUiBlock,
                    ButtonUiBlock,
                    MarkdownUiBlock,
                    ChipUiBlock,
                    SearchDropdownUiBlock,
                    UnknownType,
                ]:
                    children_item: Union[
                        TextLabelUiBlock,
                        TextInputUiBlock,
                        ButtonUiBlock,
                        MarkdownUiBlock,
                        ChipUiBlock,
                        SearchDropdownUiBlock,
                        UnknownType,
                    ]
                    discriminator_value: str = cast(str, data.get("type"))
                    if discriminator_value is not None:
                        if discriminator_value == "BUTTON":
                            children_item = ButtonUiBlock.from_dict(data)

                            return children_item
                        if discriminator_value == "CHIP":
                            children_item = ChipUiBlock.from_dict(data)

                            return children_item
                        if discriminator_value == "LABEL":
                            children_item = TextLabelUiBlock.from_dict(data)

                            return children_item
                        if discriminator_value == "MARKDOWN":
                            children_item = MarkdownUiBlock.from_dict(data)

                            return children_item
                        if discriminator_value == "SEARCH_DROPDOWN":
                            children_item = SearchDropdownUiBlock.from_dict(data)

                            return children_item
                        if discriminator_value == "TEXT_INPUT":
                            children_item = TextInputUiBlock.from_dict(data)

                            return children_item

                        return UnknownType(value=data)
                    try:
                        if not isinstance(data, dict):
                            raise TypeError()
                        children_item = TextLabelUiBlock.from_dict(data)

                        return children_item
                    except:  # noqa: E722
                        pass
                    try:
                        if not isinstance(data, dict):
                            raise TypeError()
                        children_item = TextInputUiBlock.from_dict(data)

                        return children_item
                    except:  # noqa: E722
                        pass
                    try:
                        if not isinstance(data, dict):
                            raise TypeError()
                        children_item = ButtonUiBlock.from_dict(data)

                        return children_item
                    except:  # noqa: E722
                        pass
                    try:
                        if not isinstance(data, dict):
                            raise TypeError()
                        children_item = MarkdownUiBlock.from_dict(data)

                        return children_item
                    except:  # noqa: E722
                        pass
                    try:
                        if not isinstance(data, dict):
                            raise TypeError()
                        children_item = ChipUiBlock.from_dict(data)

                        return children_item
                    except:  # noqa: E722
                        pass
                    try:
                        if not isinstance(data, dict):
                            raise TypeError()
                        children_item = SearchDropdownUiBlock.from_dict(data)

                        return children_item
                    except:  # noqa: E722
                        pass
                    return UnknownType(data)

                children_item = _parse_children_item(children_item_data)

                children.append(children_item)

            return children

        children = (
            get_children()
            if "children" in d
            else cast(
                List[
                    Union[
                        TextLabelUiBlock,
                        TextInputUiBlock,
                        ButtonUiBlock,
                        MarkdownUiBlock,
                        ChipUiBlock,
                        SearchDropdownUiBlock,
                        UnknownType,
                    ]
                ],
                UNSET,
            )
        )

        canvas_leaf_node_ui_block_list = cls(
            children=children,
        )

        canvas_leaf_node_ui_block_list.additional_properties = d
        return canvas_leaf_node_ui_block_list

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
    def children(
        self,
    ) -> List[
        Union[
            TextLabelUiBlock,
            TextInputUiBlock,
            ButtonUiBlock,
            MarkdownUiBlock,
            ChipUiBlock,
            SearchDropdownUiBlock,
            UnknownType,
        ]
    ]:
        if isinstance(self._children, Unset):
            raise NotPresentError(self, "children")
        return self._children

    @children.setter
    def children(
        self,
        value: List[
            Union[
                TextLabelUiBlock,
                TextInputUiBlock,
                ButtonUiBlock,
                MarkdownUiBlock,
                ChipUiBlock,
                SearchDropdownUiBlock,
                UnknownType,
            ]
        ],
    ) -> None:
        self._children = value
