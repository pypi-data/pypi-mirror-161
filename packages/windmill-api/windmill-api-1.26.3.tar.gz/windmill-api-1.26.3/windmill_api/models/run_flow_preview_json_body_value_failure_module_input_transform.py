from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.run_flow_preview_json_body_value_failure_module_input_transform_additional_property_type_0 import (
    RunFlowPreviewJsonBodyValueFailureModuleInputTransformAdditionalPropertyType0,
)
from ..models.run_flow_preview_json_body_value_failure_module_input_transform_additional_property_type_1 import (
    RunFlowPreviewJsonBodyValueFailureModuleInputTransformAdditionalPropertyType1,
)

T = TypeVar("T", bound="RunFlowPreviewJsonBodyValueFailureModuleInputTransform")


@attr.s(auto_attribs=True)
class RunFlowPreviewJsonBodyValueFailureModuleInputTransform:
    """ """

    additional_properties: Dict[
        str,
        Union[
            RunFlowPreviewJsonBodyValueFailureModuleInputTransformAdditionalPropertyType0,
            RunFlowPreviewJsonBodyValueFailureModuleInputTransformAdditionalPropertyType1,
        ],
    ] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:

        field_dict: Dict[str, Any] = {}
        for prop_name, prop in self.additional_properties.items():
            if isinstance(prop, RunFlowPreviewJsonBodyValueFailureModuleInputTransformAdditionalPropertyType0):
                field_dict[prop_name] = prop.to_dict()

            else:
                field_dict[prop_name] = prop.to_dict()

        field_dict.update({})

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        run_flow_preview_json_body_value_failure_module_input_transform = cls()

        additional_properties = {}
        for prop_name, prop_dict in d.items():

            def _parse_additional_property(
                data: object,
            ) -> Union[
                RunFlowPreviewJsonBodyValueFailureModuleInputTransformAdditionalPropertyType0,
                RunFlowPreviewJsonBodyValueFailureModuleInputTransformAdditionalPropertyType1,
            ]:
                try:
                    additional_property_type_0: RunFlowPreviewJsonBodyValueFailureModuleInputTransformAdditionalPropertyType0
                    if not isinstance(data, dict):
                        raise TypeError()
                    additional_property_type_0 = (
                        RunFlowPreviewJsonBodyValueFailureModuleInputTransformAdditionalPropertyType0.from_dict(data)
                    )

                    return additional_property_type_0
                except:  # noqa: E722
                    pass
                if not isinstance(data, dict):
                    raise TypeError()
                additional_property_type_1: RunFlowPreviewJsonBodyValueFailureModuleInputTransformAdditionalPropertyType1
                additional_property_type_1 = (
                    RunFlowPreviewJsonBodyValueFailureModuleInputTransformAdditionalPropertyType1.from_dict(data)
                )

                return additional_property_type_1

            additional_property = _parse_additional_property(prop_dict)

            additional_properties[prop_name] = additional_property

        run_flow_preview_json_body_value_failure_module_input_transform.additional_properties = additional_properties
        return run_flow_preview_json_body_value_failure_module_input_transform

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(
        self, key: str
    ) -> Union[
        RunFlowPreviewJsonBodyValueFailureModuleInputTransformAdditionalPropertyType0,
        RunFlowPreviewJsonBodyValueFailureModuleInputTransformAdditionalPropertyType1,
    ]:
        return self.additional_properties[key]

    def __setitem__(
        self,
        key: str,
        value: Union[
            RunFlowPreviewJsonBodyValueFailureModuleInputTransformAdditionalPropertyType0,
            RunFlowPreviewJsonBodyValueFailureModuleInputTransformAdditionalPropertyType1,
        ],
    ) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
