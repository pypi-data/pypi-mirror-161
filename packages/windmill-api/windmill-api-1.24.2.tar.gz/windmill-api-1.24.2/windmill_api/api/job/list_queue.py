import datetime
from typing import Any, Dict, List, Optional, Union

import httpx

from ...client import Client
from ...models.list_queue_response_200_item import ListQueueResponse200Item
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    client: Client,
    workspace: str,
    order_desc: Union[Unset, bool] = UNSET,
    created_by: Union[Unset, str] = UNSET,
    parent_job: Union[Unset, str] = UNSET,
    script_path_exact: Union[Unset, str] = UNSET,
    script_path_start: Union[Unset, str] = UNSET,
    script_hash: Union[Unset, str] = UNSET,
    created_before: Union[Unset, datetime.datetime] = UNSET,
    created_after: Union[Unset, datetime.datetime] = UNSET,
    success: Union[Unset, bool] = UNSET,
    job_kinds: Union[Unset, str] = UNSET,
) -> Dict[str, Any]:
    url = "{}/w/{workspace}/jobs/queue/list".format(client.base_url, workspace=workspace)

    headers: Dict[str, Any] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    json_created_before: Union[Unset, str] = UNSET
    if not isinstance(created_before, Unset):
        json_created_before = created_before.isoformat()

    json_created_after: Union[Unset, str] = UNSET
    if not isinstance(created_after, Unset):
        json_created_after = created_after.isoformat()

    params: Dict[str, Any] = {
        "order_desc": order_desc,
        "created_by": created_by,
        "parent_job": parent_job,
        "script_path_exact": script_path_exact,
        "script_path_start": script_path_start,
        "script_hash": script_hash,
        "created_before": json_created_before,
        "created_after": json_created_after,
        "success": success,
        "job_kinds": job_kinds,
    }
    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    return {
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
        "params": params,
    }


def _parse_response(*, response: httpx.Response) -> Optional[List[ListQueueResponse200Item]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = ListQueueResponse200Item.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    return None


def _build_response(*, response: httpx.Response) -> Response[List[ListQueueResponse200Item]]:
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
    order_desc: Union[Unset, bool] = UNSET,
    created_by: Union[Unset, str] = UNSET,
    parent_job: Union[Unset, str] = UNSET,
    script_path_exact: Union[Unset, str] = UNSET,
    script_path_start: Union[Unset, str] = UNSET,
    script_hash: Union[Unset, str] = UNSET,
    created_before: Union[Unset, datetime.datetime] = UNSET,
    created_after: Union[Unset, datetime.datetime] = UNSET,
    success: Union[Unset, bool] = UNSET,
    job_kinds: Union[Unset, str] = UNSET,
) -> Response[List[ListQueueResponse200Item]]:
    kwargs = _get_kwargs(
        client=client,
        workspace=workspace,
        order_desc=order_desc,
        created_by=created_by,
        parent_job=parent_job,
        script_path_exact=script_path_exact,
        script_path_start=script_path_start,
        script_hash=script_hash,
        created_before=created_before,
        created_after=created_after,
        success=success,
        job_kinds=job_kinds,
    )

    response = httpx.get(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    workspace: str,
    order_desc: Union[Unset, bool] = UNSET,
    created_by: Union[Unset, str] = UNSET,
    parent_job: Union[Unset, str] = UNSET,
    script_path_exact: Union[Unset, str] = UNSET,
    script_path_start: Union[Unset, str] = UNSET,
    script_hash: Union[Unset, str] = UNSET,
    created_before: Union[Unset, datetime.datetime] = UNSET,
    created_after: Union[Unset, datetime.datetime] = UNSET,
    success: Union[Unset, bool] = UNSET,
    job_kinds: Union[Unset, str] = UNSET,
) -> Optional[List[ListQueueResponse200Item]]:
    """ """

    return sync_detailed(
        client=client,
        workspace=workspace,
        order_desc=order_desc,
        created_by=created_by,
        parent_job=parent_job,
        script_path_exact=script_path_exact,
        script_path_start=script_path_start,
        script_hash=script_hash,
        created_before=created_before,
        created_after=created_after,
        success=success,
        job_kinds=job_kinds,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    workspace: str,
    order_desc: Union[Unset, bool] = UNSET,
    created_by: Union[Unset, str] = UNSET,
    parent_job: Union[Unset, str] = UNSET,
    script_path_exact: Union[Unset, str] = UNSET,
    script_path_start: Union[Unset, str] = UNSET,
    script_hash: Union[Unset, str] = UNSET,
    created_before: Union[Unset, datetime.datetime] = UNSET,
    created_after: Union[Unset, datetime.datetime] = UNSET,
    success: Union[Unset, bool] = UNSET,
    job_kinds: Union[Unset, str] = UNSET,
) -> Response[List[ListQueueResponse200Item]]:
    kwargs = _get_kwargs(
        client=client,
        workspace=workspace,
        order_desc=order_desc,
        created_by=created_by,
        parent_job=parent_job,
        script_path_exact=script_path_exact,
        script_path_start=script_path_start,
        script_hash=script_hash,
        created_before=created_before,
        created_after=created_after,
        success=success,
        job_kinds=job_kinds,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    workspace: str,
    order_desc: Union[Unset, bool] = UNSET,
    created_by: Union[Unset, str] = UNSET,
    parent_job: Union[Unset, str] = UNSET,
    script_path_exact: Union[Unset, str] = UNSET,
    script_path_start: Union[Unset, str] = UNSET,
    script_hash: Union[Unset, str] = UNSET,
    created_before: Union[Unset, datetime.datetime] = UNSET,
    created_after: Union[Unset, datetime.datetime] = UNSET,
    success: Union[Unset, bool] = UNSET,
    job_kinds: Union[Unset, str] = UNSET,
) -> Optional[List[ListQueueResponse200Item]]:
    """ """

    return (
        await asyncio_detailed(
            client=client,
            workspace=workspace,
            order_desc=order_desc,
            created_by=created_by,
            parent_job=parent_job,
            script_path_exact=script_path_exact,
            script_path_start=script_path_start,
            script_hash=script_hash,
            created_before=created_before,
            created_after=created_after,
            success=success,
            job_kinds=job_kinds,
        )
    ).parsed
