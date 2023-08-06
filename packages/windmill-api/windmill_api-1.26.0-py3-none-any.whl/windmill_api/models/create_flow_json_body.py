from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.create_flow_json_body_schema import CreateFlowJsonBodySchema
from ..models.create_flow_json_body_value import CreateFlowJsonBodyValue
from ..types import UNSET, Unset

T = TypeVar("T", bound="CreateFlowJsonBody")


@attr.s(auto_attribs=True)
class CreateFlowJsonBody:
    """ """

    path: str
    summary: str
    description: str
    value: CreateFlowJsonBodyValue
    schema: Union[Unset, CreateFlowJsonBodySchema] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        path = self.path
        summary = self.summary
        description = self.description
        value = self.value.to_dict()

        schema: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.schema, Unset):
            schema = self.schema.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "path": path,
                "summary": summary,
                "description": description,
                "value": value,
            }
        )
        if schema is not UNSET:
            field_dict["schema"] = schema

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        path = d.pop("path")

        summary = d.pop("summary")

        description = d.pop("description")

        value = CreateFlowJsonBodyValue.from_dict(d.pop("value"))

        schema: Union[Unset, CreateFlowJsonBodySchema] = UNSET
        _schema = d.pop("schema", UNSET)
        if not isinstance(_schema, Unset):
            schema = CreateFlowJsonBodySchema.from_dict(_schema)

        create_flow_json_body = cls(
            path=path,
            summary=summary,
            description=description,
            value=value,
            schema=schema,
        )

        create_flow_json_body.additional_properties = d
        return create_flow_json_body

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
