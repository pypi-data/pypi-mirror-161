from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.get_flow_by_path_response_200_value_failure_module_input_transform import (
    GetFlowByPathResponse200ValueFailureModuleInputTransform,
)
from ..models.get_flow_by_path_response_200_value_failure_module_value_type_0 import (
    GetFlowByPathResponse200ValueFailureModuleValueType0,
)
from ..models.get_flow_by_path_response_200_value_failure_module_value_type_1 import (
    GetFlowByPathResponse200ValueFailureModuleValueType1,
)
from ..models.get_flow_by_path_response_200_value_failure_module_value_type_2 import (
    GetFlowByPathResponse200ValueFailureModuleValueType2,
)
from ..models.get_flow_by_path_response_200_value_failure_module_value_type_3 import (
    GetFlowByPathResponse200ValueFailureModuleValueType3,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="GetFlowByPathResponse200ValueFailureModule")


@attr.s(auto_attribs=True)
class GetFlowByPathResponse200ValueFailureModule:
    """ """

    input_transform: GetFlowByPathResponse200ValueFailureModuleInputTransform
    value: Union[
        GetFlowByPathResponse200ValueFailureModuleValueType0,
        GetFlowByPathResponse200ValueFailureModuleValueType1,
        GetFlowByPathResponse200ValueFailureModuleValueType2,
        GetFlowByPathResponse200ValueFailureModuleValueType3,
    ]
    stop_after_if_expr: Union[Unset, str] = UNSET
    skip_if_stopped: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        input_transform = self.input_transform.to_dict()

        if isinstance(self.value, GetFlowByPathResponse200ValueFailureModuleValueType0):
            value = self.value.to_dict()

        elif isinstance(self.value, GetFlowByPathResponse200ValueFailureModuleValueType1):
            value = self.value.to_dict()

        elif isinstance(self.value, GetFlowByPathResponse200ValueFailureModuleValueType2):
            value = self.value.to_dict()

        else:
            value = self.value.to_dict()

        stop_after_if_expr = self.stop_after_if_expr
        skip_if_stopped = self.skip_if_stopped

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "input_transform": input_transform,
                "value": value,
            }
        )
        if stop_after_if_expr is not UNSET:
            field_dict["stop_after_if_expr"] = stop_after_if_expr
        if skip_if_stopped is not UNSET:
            field_dict["skip_if_stopped"] = skip_if_stopped

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        input_transform = GetFlowByPathResponse200ValueFailureModuleInputTransform.from_dict(d.pop("input_transform"))

        def _parse_value(
            data: object,
        ) -> Union[
            GetFlowByPathResponse200ValueFailureModuleValueType0,
            GetFlowByPathResponse200ValueFailureModuleValueType1,
            GetFlowByPathResponse200ValueFailureModuleValueType2,
            GetFlowByPathResponse200ValueFailureModuleValueType3,
        ]:
            try:
                value_type_0: GetFlowByPathResponse200ValueFailureModuleValueType0
                if not isinstance(data, dict):
                    raise TypeError()
                value_type_0 = GetFlowByPathResponse200ValueFailureModuleValueType0.from_dict(data)

                return value_type_0
            except:  # noqa: E722
                pass
            try:
                value_type_1: GetFlowByPathResponse200ValueFailureModuleValueType1
                if not isinstance(data, dict):
                    raise TypeError()
                value_type_1 = GetFlowByPathResponse200ValueFailureModuleValueType1.from_dict(data)

                return value_type_1
            except:  # noqa: E722
                pass
            try:
                value_type_2: GetFlowByPathResponse200ValueFailureModuleValueType2
                if not isinstance(data, dict):
                    raise TypeError()
                value_type_2 = GetFlowByPathResponse200ValueFailureModuleValueType2.from_dict(data)

                return value_type_2
            except:  # noqa: E722
                pass
            if not isinstance(data, dict):
                raise TypeError()
            value_type_3: GetFlowByPathResponse200ValueFailureModuleValueType3
            value_type_3 = GetFlowByPathResponse200ValueFailureModuleValueType3.from_dict(data)

            return value_type_3

        value = _parse_value(d.pop("value"))

        stop_after_if_expr = d.pop("stop_after_if_expr", UNSET)

        skip_if_stopped = d.pop("skip_if_stopped", UNSET)

        get_flow_by_path_response_200_value_failure_module = cls(
            input_transform=input_transform,
            value=value,
            stop_after_if_expr=stop_after_if_expr,
            skip_if_stopped=skip_if_stopped,
        )

        get_flow_by_path_response_200_value_failure_module.additional_properties = d
        return get_flow_by_path_response_200_value_failure_module

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
