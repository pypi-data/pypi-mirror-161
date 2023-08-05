from typing import Any, Dict, Optional

import httpx

from ...client import Client
from ...models.get_granular_acls_kind import GetGranularAclsKind
from ...models.get_granular_acls_response_200 import GetGranularAclsResponse200
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    workspace: str,
    path: str,
    kind: GetGranularAclsKind,
) -> Dict[str, Any]:
    url = "{}/w/{workspace}/acls/get/{kind}/{path}".format(client.base_url, workspace=workspace, path=path, kind=kind)

    headers: Dict[str, Any] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    return {
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
    }


def _parse_response(*, response: httpx.Response) -> Optional[GetGranularAclsResponse200]:
    if response.status_code == 200:
        response_200 = GetGranularAclsResponse200.from_dict(response.json())

        return response_200
    return None


def _build_response(*, response: httpx.Response) -> Response[GetGranularAclsResponse200]:
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
    kind: GetGranularAclsKind,
) -> Response[GetGranularAclsResponse200]:
    kwargs = _get_kwargs(
        client=client,
        workspace=workspace,
        path=path,
        kind=kind,
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
    kind: GetGranularAclsKind,
) -> Optional[GetGranularAclsResponse200]:
    """ """

    return sync_detailed(
        client=client,
        workspace=workspace,
        path=path,
        kind=kind,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    workspace: str,
    path: str,
    kind: GetGranularAclsKind,
) -> Response[GetGranularAclsResponse200]:
    kwargs = _get_kwargs(
        client=client,
        workspace=workspace,
        path=path,
        kind=kind,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    workspace: str,
    path: str,
    kind: GetGranularAclsKind,
) -> Optional[GetGranularAclsResponse200]:
    """ """

    return (
        await asyncio_detailed(
            client=client,
            workspace=workspace,
            path=path,
            kind=kind,
        )
    ).parsed
