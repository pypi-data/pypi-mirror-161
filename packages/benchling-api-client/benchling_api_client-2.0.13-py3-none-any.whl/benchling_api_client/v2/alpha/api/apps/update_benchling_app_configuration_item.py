from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.app_config_item import AppConfigItem
from ...models.forbidden_error import ForbiddenError
from ...models.not_found_error import NotFoundError
from ...models.update_app_config_item import UpdateAppConfigItem
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    item_id: str,
    json_body: UpdateAppConfigItem,
) -> Dict[str, Any]:
    url = "{}/app-configuration-items/{item_id}".format(client.base_url, item_id=item_id)

    headers: Dict[str, Any] = client.httpx_client.headers
    headers.update(client.get_headers())

    cookies: Dict[str, Any] = client.httpx_client.cookies
    cookies.update(client.get_cookies())

    json_json_body = json_body.to_dict()

    return {
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
        "json": json_json_body,
    }


def _parse_response(
    *, response: httpx.Response
) -> Optional[Union[AppConfigItem, ForbiddenError, NotFoundError]]:
    if response.status_code == 200:
        response_200 = AppConfigItem.from_dict(response.json())

        return response_200
    if response.status_code == 403:
        response_403 = ForbiddenError.from_dict(response.json())

        return response_403
    if response.status_code == 404:
        response_404 = NotFoundError.from_dict(response.json())

        return response_404
    return None


def _build_response(
    *, response: httpx.Response
) -> Response[Union[AppConfigItem, ForbiddenError, NotFoundError]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    item_id: str,
    json_body: UpdateAppConfigItem,
) -> Response[Union[AppConfigItem, ForbiddenError, NotFoundError]]:
    kwargs = _get_kwargs(
        client=client,
        item_id=item_id,
        json_body=json_body,
    )

    response = client.httpx_client.patch(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    item_id: str,
    json_body: UpdateAppConfigItem,
) -> Optional[Union[AppConfigItem, ForbiddenError, NotFoundError]]:
    """ Update app configuration item """

    return sync_detailed(
        client=client,
        item_id=item_id,
        json_body=json_body,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    item_id: str,
    json_body: UpdateAppConfigItem,
) -> Response[Union[AppConfigItem, ForbiddenError, NotFoundError]]:
    kwargs = _get_kwargs(
        client=client,
        item_id=item_id,
        json_body=json_body,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.patch(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    item_id: str,
    json_body: UpdateAppConfigItem,
) -> Optional[Union[AppConfigItem, ForbiddenError, NotFoundError]]:
    """ Update app configuration item """

    return (
        await asyncio_detailed(
            client=client,
            item_id=item_id,
            json_body=json_body,
        )
    ).parsed
