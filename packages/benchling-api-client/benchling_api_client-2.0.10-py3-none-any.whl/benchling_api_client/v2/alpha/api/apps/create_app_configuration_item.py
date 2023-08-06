from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.app_config_item import AppConfigItem
from ...models.bad_request_error import BadRequestError
from ...models.create_app_config_item import CreateAppConfigItem
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    json_body: CreateAppConfigItem,
) -> Dict[str, Any]:
    url = "{}/app-configuration-items".format(client.base_url)

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


def _parse_response(*, response: httpx.Response) -> Optional[Union[AppConfigItem, BadRequestError]]:
    if response.status_code == 201:
        response_201 = AppConfigItem.from_dict(response.json())

        return response_201
    if response.status_code == 400:
        response_400 = BadRequestError.from_dict(response.json())

        return response_400
    return None


def _build_response(*, response: httpx.Response) -> Response[Union[AppConfigItem, BadRequestError]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    json_body: CreateAppConfigItem,
) -> Response[Union[AppConfigItem, BadRequestError]]:
    kwargs = _get_kwargs(
        client=client,
        json_body=json_body,
    )

    response = client.httpx_client.post(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    json_body: CreateAppConfigItem,
) -> Optional[Union[AppConfigItem, BadRequestError]]:
    """ Create app configuration item """

    return sync_detailed(
        client=client,
        json_body=json_body,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    json_body: CreateAppConfigItem,
) -> Response[Union[AppConfigItem, BadRequestError]]:
    kwargs = _get_kwargs(
        client=client,
        json_body=json_body,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.post(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    json_body: CreateAppConfigItem,
) -> Optional[Union[AppConfigItem, BadRequestError]]:
    """ Create app configuration item """

    return (
        await asyncio_detailed(
            client=client,
            json_body=json_body,
        )
    ).parsed
