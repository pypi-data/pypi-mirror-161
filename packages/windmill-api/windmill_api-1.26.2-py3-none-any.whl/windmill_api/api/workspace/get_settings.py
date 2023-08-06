from typing import Any, Dict, Optional

import httpx

from ...client import Client
from ...models.get_settings_response_200 import GetSettingsResponse200
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    workspace: str,
) -> Dict[str, Any]:
    url = "{}/w/{workspace}/workspaces/get_settings".format(client.base_url, workspace=workspace)

    headers: Dict[str, Any] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    return {
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
    }


def _parse_response(*, response: httpx.Response) -> Optional[GetSettingsResponse200]:
    if response.status_code == 200:
        response_200 = GetSettingsResponse200.from_dict(response.json())

        return response_200
    return None


def _build_response(*, response: httpx.Response) -> Response[GetSettingsResponse200]:
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
) -> Response[GetSettingsResponse200]:
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
) -> Optional[GetSettingsResponse200]:
    """ """

    return sync_detailed(
        client=client,
        workspace=workspace,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    workspace: str,
) -> Response[GetSettingsResponse200]:
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
) -> Optional[GetSettingsResponse200]:
    """ """

    return (
        await asyncio_detailed(
            client=client,
            workspace=workspace,
        )
    ).parsed
