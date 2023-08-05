from typing import Any, Dict, List, Type, TypeVar

import attr

T = TypeVar("T", bound="ListHubScriptsResponse200AsksItem")


@attr.s(auto_attribs=True)
class ListHubScriptsResponse200AsksItem:
    """ """

    id: float
    ask_id: float
    summary: str
    app: str
    approved: bool
    is_trigger: bool
    votes: float
    views: float
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id
        ask_id = self.ask_id
        summary = self.summary
        app = self.app
        approved = self.approved
        is_trigger = self.is_trigger
        votes = self.votes
        views = self.views

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "ask_id": ask_id,
                "summary": summary,
                "app": app,
                "approved": approved,
                "is_trigger": is_trigger,
                "votes": votes,
                "views": views,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id")

        ask_id = d.pop("ask_id")

        summary = d.pop("summary")

        app = d.pop("app")

        approved = d.pop("approved")

        is_trigger = d.pop("is_trigger")

        votes = d.pop("votes")

        views = d.pop("views")

        list_hub_scripts_response_200_asks_item = cls(
            id=id,
            ask_id=ask_id,
            summary=summary,
            app=app,
            approved=approved,
            is_trigger=is_trigger,
            votes=votes,
            views=views,
        )

        list_hub_scripts_response_200_asks_item.additional_properties = d
        return list_hub_scripts_response_200_asks_item

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
