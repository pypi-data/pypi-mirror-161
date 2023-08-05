from typing import Any, Dict, List, Type, TypeVar, Union, cast

import attr

from ..models.create_script_json_body_language import CreateScriptJsonBodyLanguage
from ..models.create_script_json_body_schema import CreateScriptJsonBodySchema
from ..types import UNSET, Unset

T = TypeVar("T", bound="CreateScriptJsonBody")


@attr.s(auto_attribs=True)
class CreateScriptJsonBody:
    """ """

    path: str
    summary: str
    description: str
    content: str
    language: CreateScriptJsonBodyLanguage
    parent_hash: Union[Unset, str] = UNSET
    schema: Union[Unset, CreateScriptJsonBodySchema] = UNSET
    is_template: Union[Unset, bool] = UNSET
    lock: Union[Unset, List[str]] = UNSET
    is_trigger: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        path = self.path
        summary = self.summary
        description = self.description
        content = self.content
        language = self.language.value

        parent_hash = self.parent_hash
        schema: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.schema, Unset):
            schema = self.schema.to_dict()

        is_template = self.is_template
        lock: Union[Unset, List[str]] = UNSET
        if not isinstance(self.lock, Unset):
            lock = self.lock

        is_trigger = self.is_trigger

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "path": path,
                "summary": summary,
                "description": description,
                "content": content,
                "language": language,
            }
        )
        if parent_hash is not UNSET:
            field_dict["parent_hash"] = parent_hash
        if schema is not UNSET:
            field_dict["schema"] = schema
        if is_template is not UNSET:
            field_dict["is_template"] = is_template
        if lock is not UNSET:
            field_dict["lock"] = lock
        if is_trigger is not UNSET:
            field_dict["is_trigger"] = is_trigger

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        path = d.pop("path")

        summary = d.pop("summary")

        description = d.pop("description")

        content = d.pop("content")

        language = CreateScriptJsonBodyLanguage(d.pop("language"))

        parent_hash = d.pop("parent_hash", UNSET)

        schema: Union[Unset, CreateScriptJsonBodySchema] = UNSET
        _schema = d.pop("schema", UNSET)
        if not isinstance(_schema, Unset):
            schema = CreateScriptJsonBodySchema.from_dict(_schema)

        is_template = d.pop("is_template", UNSET)

        lock = cast(List[str], d.pop("lock", UNSET))

        is_trigger = d.pop("is_trigger", UNSET)

        create_script_json_body = cls(
            path=path,
            summary=summary,
            description=description,
            content=content,
            language=language,
            parent_hash=parent_hash,
            schema=schema,
            is_template=is_template,
            lock=lock,
            is_trigger=is_trigger,
        )

        create_script_json_body.additional_properties = d
        return create_script_json_body

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
