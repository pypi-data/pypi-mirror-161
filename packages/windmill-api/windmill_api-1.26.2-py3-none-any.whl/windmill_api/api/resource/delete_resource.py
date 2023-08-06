from typing import Any, Dict

import httpx

from ...client import Client
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    workspace: str,
    path: str,
) -> Dict[str, Any]:
    url = "{}/w/{workspace}/resources/delete/{path}".format(client.base_url, workspace=workspace, path=path)

    headers: Dict[str, Any] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    return {
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
    }


def _build_response(*, response: httpx.Response) -> Response[None]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=None,
    )


def sync_detailed(
    *,
    client: Client,
    workspace: str,
    path: str,
) -> Response[None]:
    kwargs = _get_kwargs(
        client=client,
        workspace=workspace,
        path=path,
    )

    response = httpx.delete(
        **kwargs,
    )

    return _build_response(response=response)


async def asyncio_detailed(
    *,
    client: Client,
    workspace: str,
    path: str,
) -> Response[None]:
    kwargs = _get_kwargs(
        client=client,
        workspace=workspace,
        path=path,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.delete(**kwargs)

    return _build_response(response=response)
