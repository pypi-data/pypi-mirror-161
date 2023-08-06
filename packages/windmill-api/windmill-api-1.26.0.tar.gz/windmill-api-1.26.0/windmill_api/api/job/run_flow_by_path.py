import datetime
from typing import Any, Dict, Union

import httpx

from ...client import Client
from ...models.run_flow_by_path_json_body import RunFlowByPathJsonBody
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    client: Client,
    workspace: str,
    path: str,
    json_body: RunFlowByPathJsonBody,
    scheduled_for: Union[Unset, datetime.datetime] = UNSET,
    scheduled_in_secs: Union[Unset, float] = UNSET,
    parent_job: Union[Unset, str] = UNSET,
) -> Dict[str, Any]:
    url = "{}/w/{workspace}/jobs/run/f/{path}".format(client.base_url, workspace=workspace, path=path)

    headers: Dict[str, Any] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    json_scheduled_for: Union[Unset, str] = UNSET
    if not isinstance(scheduled_for, Unset):
        json_scheduled_for = scheduled_for.isoformat()

    params: Dict[str, Any] = {
        "scheduled_for": json_scheduled_for,
        "scheduled_in_secs": scheduled_in_secs,
        "parent_job": parent_job,
    }
    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    json_json_body = json_body.to_dict()

    return {
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
        "json": json_json_body,
        "params": params,
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
    json_body: RunFlowByPathJsonBody,
    scheduled_for: Union[Unset, datetime.datetime] = UNSET,
    scheduled_in_secs: Union[Unset, float] = UNSET,
    parent_job: Union[Unset, str] = UNSET,
) -> Response[None]:
    kwargs = _get_kwargs(
        client=client,
        workspace=workspace,
        path=path,
        json_body=json_body,
        scheduled_for=scheduled_for,
        scheduled_in_secs=scheduled_in_secs,
        parent_job=parent_job,
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
    json_body: RunFlowByPathJsonBody,
    scheduled_for: Union[Unset, datetime.datetime] = UNSET,
    scheduled_in_secs: Union[Unset, float] = UNSET,
    parent_job: Union[Unset, str] = UNSET,
) -> Response[None]:
    kwargs = _get_kwargs(
        client=client,
        workspace=workspace,
        path=path,
        json_body=json_body,
        scheduled_for=scheduled_for,
        scheduled_in_secs=scheduled_in_secs,
        parent_job=parent_job,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.post(**kwargs)

    return _build_response(response=response)
