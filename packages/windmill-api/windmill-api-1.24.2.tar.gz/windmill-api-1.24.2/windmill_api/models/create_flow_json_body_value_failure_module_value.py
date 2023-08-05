from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.create_flow_json_body_value_failure_module_value_iterator import (
    CreateFlowJsonBodyValueFailureModuleValueIterator,
)
from ..models.create_flow_json_body_value_failure_module_value_language import (
    CreateFlowJsonBodyValueFailureModuleValueLanguage,
)
from ..models.create_flow_json_body_value_failure_module_value_type import CreateFlowJsonBodyValueFailureModuleValueType
from ..types import UNSET, Unset

T = TypeVar("T", bound="CreateFlowJsonBodyValueFailureModuleValue")


@attr.s(auto_attribs=True)
class CreateFlowJsonBodyValueFailureModuleValue:
    """ """

    type: CreateFlowJsonBodyValueFailureModuleValueType
    iterator: Union[Unset, CreateFlowJsonBodyValueFailureModuleValueIterator] = UNSET
    skip_failures: Union[Unset, bool] = UNSET
    path: Union[Unset, str] = UNSET
    content: Union[Unset, str] = UNSET
    language: Union[Unset, CreateFlowJsonBodyValueFailureModuleValueLanguage] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        type = self.type.value

        iterator: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.iterator, Unset):
            iterator = self.iterator.to_dict()

        skip_failures = self.skip_failures
        path = self.path
        content = self.content
        language: Union[Unset, str] = UNSET
        if not isinstance(self.language, Unset):
            language = self.language.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type,
            }
        )
        if iterator is not UNSET:
            field_dict["iterator"] = iterator
        if skip_failures is not UNSET:
            field_dict["skip_failures"] = skip_failures
        if path is not UNSET:
            field_dict["path"] = path
        if content is not UNSET:
            field_dict["content"] = content
        if language is not UNSET:
            field_dict["language"] = language

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        type = CreateFlowJsonBodyValueFailureModuleValueType(d.pop("type"))

        iterator: Union[Unset, CreateFlowJsonBodyValueFailureModuleValueIterator] = UNSET
        _iterator = d.pop("iterator", UNSET)
        if not isinstance(_iterator, Unset):
            iterator = CreateFlowJsonBodyValueFailureModuleValueIterator.from_dict(_iterator)

        skip_failures = d.pop("skip_failures", UNSET)

        path = d.pop("path", UNSET)

        content = d.pop("content", UNSET)

        language: Union[Unset, CreateFlowJsonBodyValueFailureModuleValueLanguage] = UNSET
        _language = d.pop("language", UNSET)
        if not isinstance(_language, Unset):
            language = CreateFlowJsonBodyValueFailureModuleValueLanguage(_language)

        create_flow_json_body_value_failure_module_value = cls(
            type=type,
            iterator=iterator,
            skip_failures=skip_failures,
            path=path,
            content=content,
            language=language,
        )

        create_flow_json_body_value_failure_module_value.additional_properties = d
        return create_flow_json_body_value_failure_module_value

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
