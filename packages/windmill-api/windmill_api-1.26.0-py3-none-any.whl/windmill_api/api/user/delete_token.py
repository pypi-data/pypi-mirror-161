from typing import Any, Dict

import httpx

from ...client import Client
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    token_prefix: str,
) -> Dict[str, Any]:
    url = "{}/users/tokens/delete/{token_prefix}".format(client.base_url, token_prefix=token_prefix)

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
    token_prefix: str,
) -> Response[None]:
    kwargs = _get_kwargs(
        client=client,
        token_prefix=token_prefix,
    )

    response = httpx.delete(
        **kwargs,
    )

    return _build_response(response=response)


async def asyncio_detailed(
    *,
    client: Client,
    token_prefix: str,
) -> Response[None]:
    kwargs = _get_kwargs(
        client=client,
        token_prefix=token_prefix,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.delete(**kwargs)

    return _build_response(response=response)
