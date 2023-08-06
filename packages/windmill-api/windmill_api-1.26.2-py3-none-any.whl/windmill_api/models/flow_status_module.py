from typing import Any, Dict, List, Type, TypeVar, Union, cast

import attr

from ..models.flow_status_module_iterator import FlowStatusModuleIterator
from ..models.flow_status_module_type import FlowStatusModuleType
from ..types import UNSET, Unset

T = TypeVar("T", bound="FlowStatusModule")


@attr.s(auto_attribs=True)
class FlowStatusModule:
    """ """

    type: FlowStatusModuleType
    job: Union[Unset, str] = UNSET
    event: Union[Unset, str] = UNSET
    iterator: Union[Unset, FlowStatusModuleIterator] = UNSET
    forloop_jobs: Union[Unset, List[str]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        type = self.type.value

        job = self.job
        event = self.event
        iterator: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.iterator, Unset):
            iterator = self.iterator.to_dict()

        forloop_jobs: Union[Unset, List[str]] = UNSET
        if not isinstance(self.forloop_jobs, Unset):
            forloop_jobs = self.forloop_jobs

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type,
            }
        )
        if job is not UNSET:
            field_dict["job"] = job
        if event is not UNSET:
            field_dict["event"] = event
        if iterator is not UNSET:
            field_dict["iterator"] = iterator
        if forloop_jobs is not UNSET:
            field_dict["forloop_jobs"] = forloop_jobs

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        type = FlowStatusModuleType(d.pop("type"))

        job = d.pop("job", UNSET)

        event = d.pop("event", UNSET)

        iterator: Union[Unset, FlowStatusModuleIterator] = UNSET
        _iterator = d.pop("iterator", UNSET)
        if not isinstance(_iterator, Unset):
            iterator = FlowStatusModuleIterator.from_dict(_iterator)

        forloop_jobs = cast(List[str], d.pop("forloop_jobs", UNSET))

        flow_status_module = cls(
            type=type,
            job=job,
            event=event,
            iterator=iterator,
            forloop_jobs=forloop_jobs,
        )

        flow_status_module.additional_properties = d
        return flow_status_module

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
