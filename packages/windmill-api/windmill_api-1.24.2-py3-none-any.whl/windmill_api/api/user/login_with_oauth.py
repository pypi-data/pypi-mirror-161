from typing import Any, Dict

import httpx

from ...client import Client
from ...models.login_with_oauth_json_body import LoginWithOauthJsonBody
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    client_name: str,
    json_body: LoginWithOauthJsonBody,
) -> Dict[str, Any]:
    url = "{}/oauth/login_callback/{client_name}".format(client.base_url, client_name=client_name)

    headers: Dict[str, Any] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    json_json_body = json_body.to_dict()

    return {
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
        "json": json_json_body,
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
    client_name: str,
    json_body: LoginWithOauthJsonBody,
) -> Response[None]:
    kwargs = _get_kwargs(
        client=client,
        client_name=client_name,
        json_body=json_body,
    )

    response = httpx.post(
        **kwargs,
    )

    return _build_response(response=response)


async def asyncio_detailed(
    *,
    client: Client,
    client_name: str,
    json_body: LoginWithOauthJsonBody,
) -> Response[None]:
    kwargs = _get_kwargs(
        client=client,
        client_name=client_name,
        json_body=json_body,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.post(**kwargs)

    return _build_response(response=response)
