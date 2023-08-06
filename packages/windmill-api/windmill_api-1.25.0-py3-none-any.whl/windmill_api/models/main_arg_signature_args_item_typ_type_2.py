from typing import Any, Dict, List, Type, TypeVar

import attr

from ..models.main_arg_signature_args_item_typ_type_2_list import MainArgSignatureArgsItemTypType2List

T = TypeVar("T", bound="MainArgSignatureArgsItemTypType2")


@attr.s(auto_attribs=True)
class MainArgSignatureArgsItemTypType2:
    """ """

    list_: MainArgSignatureArgsItemTypType2List
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        list_ = self.list_.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "list": list_,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        list_ = MainArgSignatureArgsItemTypType2List(d.pop("list"))

        main_arg_signature_args_item_typ_type_2 = cls(
            list_=list_,
        )

        main_arg_signature_args_item_typ_type_2.additional_properties = d
        return main_arg_signature_args_item_typ_type_2

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
