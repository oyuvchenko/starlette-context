import pytest
from starlette import status
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.testclient import TestClient

from starlette_context import context, plugins
from starlette_context.header_keys import HeaderKeys
from starlette_context.middleware import RawContextMiddleware


async def index(request: Request) -> JSONResponse:
    return JSONResponse(content=context.data)


plugins_to_use = (
    plugins.CorrelationIdPlugin(),
    plugins.RequestIdPlugin(),
    plugins.UserAgentPlugin(),
    plugins.ForwardedForPlugin(),
    plugins.DateHeaderPlugin(),
)

app = Starlette(
    routes=[
        Route("/", index),
    ],
    middleware=[
        Middleware(
            RawContextMiddleware,
            plugins=plugins_to_use,
        )
    ],
)


@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client


def test_valid_request(client):
    resp = client.get("/")

    assert resp.status_code == status.HTTP_200_OK

    for plugin in plugins_to_use:
        assert plugin.key in resp.text

    assert HeaderKeys.correlation_id in resp.headers
    assert HeaderKeys.request_id in resp.headers
