from typing import Any, Dict, List, Optional, Union

import httpx

from ...client import Client
from ...models.list_scripts_response_200_item import ListScriptsResponse200Item
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    client: Client,
    workspace: str,
    page: Union[Unset, int] = UNSET,
    per_page: Union[Unset, int] = UNSET,
    order_desc: Union[Unset, bool] = UNSET,
    created_by: Union[Unset, str] = UNSET,
    path_start: Union[Unset, str] = UNSET,
    path_exact: Union[Unset, str] = UNSET,
    first_parent_hash: Union[Unset, str] = UNSET,
    last_parent_hash: Union[Unset, str] = UNSET,
    parent_hash: Union[Unset, str] = UNSET,
    show_archived: Union[Unset, bool] = UNSET,
    is_template: Union[Unset, bool] = UNSET,
    is_trigger: Union[Unset, bool] = UNSET,
) -> Dict[str, Any]:
    url = "{}/w/{workspace}/scripts/list".format(client.base_url, workspace=workspace)

    headers: Dict[str, Any] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    params: Dict[str, Any] = {
        "page": page,
        "per_page": per_page,
        "order_desc": order_desc,
        "created_by": created_by,
        "path_start": path_start,
        "path_exact": path_exact,
        "first_parent_hash": first_parent_hash,
        "last_parent_hash": last_parent_hash,
        "parent_hash": parent_hash,
        "show_archived": show_archived,
        "is_template": is_template,
        "is_trigger": is_trigger,
    }
    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    return {
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
        "params": params,
    }


def _parse_response(*, response: httpx.Response) -> Optional[List[ListScriptsResponse200Item]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = ListScriptsResponse200Item.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    return None


def _build_response(*, response: httpx.Response) -> Response[List[ListScriptsResponse200Item]]:
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
    order_desc: Union[Unset, bool] = UNSET,
    created_by: Union[Unset, str] = UNSET,
    path_start: Union[Unset, str] = UNSET,
    path_exact: Union[Unset, str] = UNSET,
    first_parent_hash: Union[Unset, str] = UNSET,
    last_parent_hash: Union[Unset, str] = UNSET,
    parent_hash: Union[Unset, str] = UNSET,
    show_archived: Union[Unset, bool] = UNSET,
    is_template: Union[Unset, bool] = UNSET,
    is_trigger: Union[Unset, bool] = UNSET,
) -> Response[List[ListScriptsResponse200Item]]:
    kwargs = _get_kwargs(
        client=client,
        workspace=workspace,
        page=page,
        per_page=per_page,
        order_desc=order_desc,
        created_by=created_by,
        path_start=path_start,
        path_exact=path_exact,
        first_parent_hash=first_parent_hash,
        last_parent_hash=last_parent_hash,
        parent_hash=parent_hash,
        show_archived=show_archived,
        is_template=is_template,
        is_trigger=is_trigger,
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
    order_desc: Union[Unset, bool] = UNSET,
    created_by: Union[Unset, str] = UNSET,
    path_start: Union[Unset, str] = UNSET,
    path_exact: Union[Unset, str] = UNSET,
    first_parent_hash: Union[Unset, str] = UNSET,
    last_parent_hash: Union[Unset, str] = UNSET,
    parent_hash: Union[Unset, str] = UNSET,
    show_archived: Union[Unset, bool] = UNSET,
    is_template: Union[Unset, bool] = UNSET,
    is_trigger: Union[Unset, bool] = UNSET,
) -> Optional[List[ListScriptsResponse200Item]]:
    """ """

    return sync_detailed(
        client=client,
        workspace=workspace,
        page=page,
        per_page=per_page,
        order_desc=order_desc,
        created_by=created_by,
        path_start=path_start,
        path_exact=path_exact,
        first_parent_hash=first_parent_hash,
        last_parent_hash=last_parent_hash,
        parent_hash=parent_hash,
        show_archived=show_archived,
        is_template=is_template,
        is_trigger=is_trigger,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    workspace: str,
    page: Union[Unset, int] = UNSET,
    per_page: Union[Unset, int] = UNSET,
    order_desc: Union[Unset, bool] = UNSET,
    created_by: Union[Unset, str] = UNSET,
    path_start: Union[Unset, str] = UNSET,
    path_exact: Union[Unset, str] = UNSET,
    first_parent_hash: Union[Unset, str] = UNSET,
    last_parent_hash: Union[Unset, str] = UNSET,
    parent_hash: Union[Unset, str] = UNSET,
    show_archived: Union[Unset, bool] = UNSET,
    is_template: Union[Unset, bool] = UNSET,
    is_trigger: Union[Unset, bool] = UNSET,
) -> Response[List[ListScriptsResponse200Item]]:
    kwargs = _get_kwargs(
        client=client,
        workspace=workspace,
        page=page,
        per_page=per_page,
        order_desc=order_desc,
        created_by=created_by,
        path_start=path_start,
        path_exact=path_exact,
        first_parent_hash=first_parent_hash,
        last_parent_hash=last_parent_hash,
        parent_hash=parent_hash,
        show_archived=show_archived,
        is_template=is_template,
        is_trigger=is_trigger,
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
    order_desc: Union[Unset, bool] = UNSET,
    created_by: Union[Unset, str] = UNSET,
    path_start: Union[Unset, str] = UNSET,
    path_exact: Union[Unset, str] = UNSET,
    first_parent_hash: Union[Unset, str] = UNSET,
    last_parent_hash: Union[Unset, str] = UNSET,
    parent_hash: Union[Unset, str] = UNSET,
    show_archived: Union[Unset, bool] = UNSET,
    is_template: Union[Unset, bool] = UNSET,
    is_trigger: Union[Unset, bool] = UNSET,
) -> Optional[List[ListScriptsResponse200Item]]:
    """ """

    return (
        await asyncio_detailed(
            client=client,
            workspace=workspace,
            page=page,
            per_page=per_page,
            order_desc=order_desc,
            created_by=created_by,
            path_start=path_start,
            path_exact=path_exact,
            first_parent_hash=first_parent_hash,
            last_parent_hash=last_parent_hash,
            parent_hash=parent_hash,
            show_archived=show_archived,
            is_template=is_template,
            is_trigger=is_trigger,
        )
    ).parsed
