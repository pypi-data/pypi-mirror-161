from typing import Any, Dict, List, Type, TypeVar

import attr

from ..models.flow_value_modules_item_input_transform_additional_property import (
    FlowValueModulesItemInputTransformAdditionalProperty,
)

T = TypeVar("T", bound="FlowValueModulesItemInputTransform")


@attr.s(auto_attribs=True)
class FlowValueModulesItemInputTransform:
    """ """

    additional_properties: Dict[str, FlowValueModulesItemInputTransformAdditionalProperty] = attr.ib(
        init=False, factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:

        field_dict: Dict[str, Any] = {}
        for prop_name, prop in self.additional_properties.items():
            field_dict[prop_name] = prop.to_dict()

        field_dict.update({})

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        flow_value_modules_item_input_transform = cls()

        additional_properties = {}
        for prop_name, prop_dict in d.items():
            additional_property = FlowValueModulesItemInputTransformAdditionalProperty.from_dict(prop_dict)

            additional_properties[prop_name] = additional_property

        flow_value_modules_item_input_transform.additional_properties = additional_properties
        return flow_value_modules_item_input_transform

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> FlowValueModulesItemInputTransformAdditionalProperty:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: FlowValueModulesItemInputTransformAdditionalProperty) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
