from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.get_flow_by_path_response_200_value_failure_module import GetFlowByPathResponse200ValueFailureModule
from ..models.get_flow_by_path_response_200_value_modules_item import GetFlowByPathResponse200ValueModulesItem
from ..types import UNSET, Unset

T = TypeVar("T", bound="GetFlowByPathResponse200Value")


@attr.s(auto_attribs=True)
class GetFlowByPathResponse200Value:
    """ """

    modules: List[GetFlowByPathResponse200ValueModulesItem]
    failure_module: Union[Unset, GetFlowByPathResponse200ValueFailureModule] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        modules = []
        for modules_item_data in self.modules:
            modules_item = modules_item_data.to_dict()

            modules.append(modules_item)

        failure_module: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.failure_module, Unset):
            failure_module = self.failure_module.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "modules": modules,
            }
        )
        if failure_module is not UNSET:
            field_dict["failure_module"] = failure_module

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        modules = []
        _modules = d.pop("modules")
        for modules_item_data in _modules:
            modules_item = GetFlowByPathResponse200ValueModulesItem.from_dict(modules_item_data)

            modules.append(modules_item)

        failure_module: Union[Unset, GetFlowByPathResponse200ValueFailureModule] = UNSET
        _failure_module = d.pop("failure_module", UNSET)
        if not isinstance(_failure_module, Unset):
            failure_module = GetFlowByPathResponse200ValueFailureModule.from_dict(_failure_module)

        get_flow_by_path_response_200_value = cls(
            modules=modules,
            failure_module=failure_module,
        )

        get_flow_by_path_response_200_value.additional_properties = d
        return get_flow_by_path_response_200_value

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
