from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.get_job_updates_response_200 import GetJobUpdatesResponse200
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    client: Client,
    workspace: str,
    id: str,
    running: Union[Unset, bool] = UNSET,
    log_offset: Union[Unset, float] = UNSET,
) -> Dict[str, Any]:
    url = "{}/w/{workspace}/jobs/getupdate/{id}".format(client.base_url, workspace=workspace, id=id)

    headers: Dict[str, Any] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    params: Dict[str, Any] = {
        "running": running,
        "log_offset": log_offset,
    }
    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    return {
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
        "params": params,
    }


def _parse_response(*, response: httpx.Response) -> Optional[GetJobUpdatesResponse200]:
    if response.status_code == 200:
        response_200 = GetJobUpdatesResponse200.from_dict(response.json())

        return response_200
    return None


def _build_response(*, response: httpx.Response) -> Response[GetJobUpdatesResponse200]:
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
    id: str,
    running: Union[Unset, bool] = UNSET,
    log_offset: Union[Unset, float] = UNSET,
) -> Response[GetJobUpdatesResponse200]:
    kwargs = _get_kwargs(
        client=client,
        workspace=workspace,
        id=id,
        running=running,
        log_offset=log_offset,
    )

    response = httpx.get(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    workspace: str,
    id: str,
    running: Union[Unset, bool] = UNSET,
    log_offset: Union[Unset, float] = UNSET,
) -> Optional[GetJobUpdatesResponse200]:
    """ """

    return sync_detailed(
        client=client,
        workspace=workspace,
        id=id,
        running=running,
        log_offset=log_offset,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    workspace: str,
    id: str,
    running: Union[Unset, bool] = UNSET,
    log_offset: Union[Unset, float] = UNSET,
) -> Response[GetJobUpdatesResponse200]:
    kwargs = _get_kwargs(
        client=client,
        workspace=workspace,
        id=id,
        running=running,
        log_offset=log_offset,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    workspace: str,
    id: str,
    running: Union[Unset, bool] = UNSET,
    log_offset: Union[Unset, float] = UNSET,
) -> Optional[GetJobUpdatesResponse200]:
    """ """

    return (
        await asyncio_detailed(
            client=client,
            workspace=workspace,
            id=id,
            running=running,
            log_offset=log_offset,
        )
    ).parsed
