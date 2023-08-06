from typing import Any, Dict

import httpx

from ...client import Client
from ...models.remove_granular_acls_json_body import RemoveGranularAclsJsonBody
from ...models.remove_granular_acls_kind import RemoveGranularAclsKind
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    workspace: str,
    path: str,
    kind: RemoveGranularAclsKind,
    json_body: RemoveGranularAclsJsonBody,
) -> Dict[str, Any]:
    url = "{}/w/{workspace}/acls/remove/{kind}/{path}".format(
        client.base_url, workspace=workspace, path=path, kind=kind
    )

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
    workspace: str,
    path: str,
    kind: RemoveGranularAclsKind,
    json_body: RemoveGranularAclsJsonBody,
) -> Response[None]:
    kwargs = _get_kwargs(
        client=client,
        workspace=workspace,
        path=path,
        kind=kind,
        json_body=json_body,
    )

    response = httpx.post(
        **kwargs,
    )

    return _build_response(response=response)


async def asyncio_detailed(
    *,
    client: Client,
    workspace: str,
    path: str,
    kind: RemoveGranularAclsKind,
    json_body: RemoveGranularAclsJsonBody,
) -> Response[None]:
    kwargs = _get_kwargs(
        client=client,
        workspace=workspace,
        path=path,
        kind=kind,
        json_body=json_body,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.post(**kwargs)

    return _build_response(response=response)
