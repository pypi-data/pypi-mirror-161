import datetime
from typing import Any, Dict, List, Optional, Union

import httpx

from ...client import Client
from ...models.list_audit_logs_action_kind import ListAuditLogsActionKind
from ...models.list_audit_logs_response_200_item import ListAuditLogsResponse200Item
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    client: Client,
    workspace: str,
    page: Union[Unset, int] = UNSET,
    per_page: Union[Unset, int] = UNSET,
    before: Union[Unset, datetime.datetime] = UNSET,
    after: Union[Unset, datetime.datetime] = UNSET,
    username: Union[Unset, str] = UNSET,
    operation: Union[Unset, str] = UNSET,
    resource: Union[Unset, str] = UNSET,
    action_kind: Union[Unset, ListAuditLogsActionKind] = UNSET,
) -> Dict[str, Any]:
    url = "{}/w/{workspace}/audit/list".format(client.base_url, workspace=workspace)

    headers: Dict[str, Any] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    json_before: Union[Unset, str] = UNSET
    if not isinstance(before, Unset):
        json_before = before.isoformat()

    json_after: Union[Unset, str] = UNSET
    if not isinstance(after, Unset):
        json_after = after.isoformat()

    json_action_kind: Union[Unset, str] = UNSET
    if not isinstance(action_kind, Unset):
        json_action_kind = action_kind.value

    params: Dict[str, Any] = {
        "page": page,
        "per_page": per_page,
        "before": json_before,
        "after": json_after,
        "username": username,
        "operation": operation,
        "resource": resource,
        "action_kind": json_action_kind,
    }
    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    return {
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
        "params": params,
    }


def _parse_response(*, response: httpx.Response) -> Optional[List[ListAuditLogsResponse200Item]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = ListAuditLogsResponse200Item.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    return None


def _build_response(*, response: httpx.Response) -> Response[List[ListAuditLogsResponse200Item]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    workspace: str,
    page: Union[Unset, int] = UNSET,
    per_page: Union[Unset, int] = UNSET,
    before: Union[Unset, datetime.datetime] = UNSET,
    after: Union[Unset, datetime.datetime] = UNSET,
    username: Union[Unset, str] = UNSET,
    operation: Union[Unset, str] = UNSET,
    resource: Union[Unset, str] = UNSET,
    action_kind: Union[Unset, ListAuditLogsActionKind] = UNSET,
) -> Response[List[ListAuditLogsResponse200Item]]:
    kwargs = _get_kwargs(
        client=client,
        workspace=workspace,
        page=page,
        per_page=per_page,
        before=before,
        after=after,
        username=username,
        operation=operation,
        resource=resource,
        action_kind=action_kind,
    )

    response = httpx.get(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    workspace: str,
    page: Union[Unset, int] = UNSET,
    per_page: Union[Unset, int] = UNSET,
    before: Union[Unset, datetime.datetime] = UNSET,
    after: Union[Unset, datetime.datetime] = UNSET,
    username: Union[Unset, str] = UNSET,
    operation: Union[Unset, str] = UNSET,
    resource: Union[Unset, str] = UNSET,
    action_kind: Union[Unset, ListAuditLogsActionKind] = UNSET,
) -> Optional[List[ListAuditLogsResponse200Item]]:
    """ """

    return sync_detailed(
        client=client,
        workspace=workspace,
        page=page,
        per_page=per_page,
        before=before,
        after=after,
        username=username,
        operation=operation,
        resource=resource,
        action_kind=action_kind,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    workspace: str,
    page: Union[Unset, int] = UNSET,
    per_page: Union[Unset, int] = UNSET,
    before: Union[Unset, datetime.datetime] = UNSET,
    after: Union[Unset, datetime.datetime] = UNSET,
    username: Union[Unset, str] = UNSET,
    operation: Union[Unset, str] = UNSET,
    resource: Union[Unset, str] = UNSET,
    action_kind: Union[Unset, ListAuditLogsActionKind] = UNSET,
) -> Response[List[ListAuditLogsResponse200Item]]:
    kwargs = _get_kwargs(
        client=client,
        workspace=workspace,
        page=page,
        per_page=per_page,
        before=before,
        after=after,
        username=username,
        operation=operation,
        resource=resource,
        action_kind=action_kind,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    workspace: str,
    page: Union[Unset, int] = UNSET,
    per_page: Union[Unset, int] = UNSET,
    before: Union[Unset, datetime.datetime] = UNSET,
    after: Union[Unset, datetime.datetime] = UNSET,
    username: Union[Unset, str] = UNSET,
    operation: Union[Unset, str] = UNSET,
    resource: Union[Unset, str] = UNSET,
    action_kind: Union[Unset, ListAuditLogsActionKind] = UNSET,
) -> Optional[List[ListAuditLogsResponse200Item]]:
    """ """

    return (
        await asyncio_detailed(
            client=client,
            workspace=workspace,
            page=page,
            per_page=per_page,
            before=before,
            after=after,
            username=username,
            operation=operation,
            resource=resource,
            action_kind=action_kind,
        )
    ).parsed
