from typing import Any, Dict, Optional

import httpx

from ...client import Client
from ...models.get_flow_by_path_response_200 import GetFlowByPathResponse200
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    workspace: str,
    path: str,
) -> Dict[str, Any]:
    url = "{}/w/{workspace}/flows/get/{path}".format(client.base_url, workspace=workspace, path=path)

    headers: Dict[str, Any] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    return {
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
    }


def _parse_response(*, response: httpx.Response) -> Optional[GetFlowByPathResponse200]:
    if response.status_code == 200:
        response_200 = GetFlowByPathResponse200.from_dict(response.json())

        return response_200
    return None


def _build_response(*, response: httpx.Response) -> Response[GetFlowByPathResponse200]:
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
    path: str,
) -> Response[GetFlowByPathResponse200]:
    kwargs = _get_kwargs(
        client=client,
        workspace=workspace,
        path=path,
    )

    response = httpx.get(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    workspace: str,
    path: str,
) -> Optional[GetFlowByPathResponse200]:
    """ """

    return sync_detailed(
        client=client,
        workspace=workspace,
        path=path,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    workspace: str,
    path: str,
) -> Response[GetFlowByPathResponse200]:
    kwargs = _get_kwargs(
        client=client,
        workspace=workspace,
        path=path,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    workspace: str,
    path: str,
) -> Optional[GetFlowByPathResponse200]:
    """ """

    return (
        await asyncio_detailed(
            client=client,
            workspace=workspace,
            path=path,
        )
    ).parsed
