import logging

import aioredis
import pytest

from src import config, controller
from src.app import app as test_app

from tests import TEST_DB


from sanic.exceptions import MethodNotSupported

@pytest.yield_fixture
def app():
    test_app.config.DB_HOST = config.DB_HOST
    test_app.config.DB_PORT = config.DB_PORT
    logging.debug("Configured test app with DB: {}:{}".format(test_app.config.DB_HOST, test_app.config.DB_PORT))
    yield test_app


@pytest.fixture
def sanic_server(loop, app, test_server):
    app.redis = loop.run_until_complete(aioredis.create_redis(
        "redis://{}:{}".format(app.config.DB_HOST, app.config.DB_PORT),
        db=TEST_DB,
        encoding="utf-8"
    ))
    logging.debug("Test server configured with Redis instance: {}".format(app.redis))
    app.redis.flushdb()
    controller.db = app.redis
    return loop.run_until_complete(test_server(app))


def test_methods(sanic_server):
    # POST
    _, response = sanic_server.app.test_client.patch(
        "/register"
    )
    assert response.status == MethodNotSupported.status_code

    # PUT
    _, response = sanic_server.app.test_client.post(
        "/login"
    )
    assert response.status == MethodNotSupported.status_code

    # PATCH
    _, response = sanic_server.app.test_client.put(
        "/update"
    )
    assert response.status == MethodNotSupported.status_code

    # DELETE
    _, response = sanic_server.app.test_client.post(
        "/delete"
    )
    assert response.status == MethodNotSupported.status_code

    # DELETE
    _, response = sanic_server.app.test_client.post(
        "/logout"
    )
    assert response.status == MethodNotSupported.status_code
