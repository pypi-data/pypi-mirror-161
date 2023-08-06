from typing import Any, Dict, List, Optional

import httpx

from ...client import Client
from ...models.list_users_response_200_item import ListUsersResponse200Item
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    workspace: str,
) -> Dict[str, Any]:
    url = "{}/w/{workspace}/users/list".format(client.base_url, workspace=workspace)

    headers: Dict[str, Any] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    return {
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
    }


def _parse_response(*, response: httpx.Response) -> Optional[List[ListUsersResponse200Item]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = ListUsersResponse200Item.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    return None


def _build_response(*, response: httpx.Response) -> Response[List[ListUsersResponse200Item]]:
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
) -> Response[List[ListUsersResponse200Item]]:
    kwargs = _get_kwargs(
        client=client,
        workspace=workspace,
    )

    response = httpx.get(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    workspace: str,
) -> Optional[List[ListUsersResponse200Item]]:
    """ """

    return sync_detailed(
        client=client,
        workspace=workspace,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    workspace: str,
) -> Response[List[ListUsersResponse200Item]]:
    kwargs = _get_kwargs(
        client=client,
        workspace=workspace,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    workspace: str,
) -> Optional[List[ListUsersResponse200Item]]:
    """ """

    return (
        await asyncio_detailed(
            client=client,
            workspace=workspace,
        )
    ).parsed
