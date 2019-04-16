import logging

import aioredis
import pytest
from sanic.exceptions import MethodNotSupported, ServerError
import ujson

from src import config, controller
from src.app import app as test_app

from tests import TEST_DB


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
    loop.run_until_complete(app.redis.flushdb())
    controller.db = app.redis
    return loop.run_until_complete(test_server(app))


def test_methods(sanic_server):
    location = "/user"  # GET
    _, response = sanic_server.app.test_client.get(location)
    assert response.status == ServerError.status_code

    _, response = sanic_server.app.test_client.post(location)
    assert response.status == MethodNotSupported.status_code

    location = "/register"  # POST
    _, response = sanic_server.app.test_client.post(location)
    assert response.status == ServerError.status_code

    _, response = sanic_server.app.test_client.patch(location)
    assert response.status == MethodNotSupported.status_code

    location = "/login"  # PUT
    _, response = sanic_server.app.test_client.put(location)
    assert response.status == ServerError.status_code

    _, response = sanic_server.app.test_client.post(location)
    assert response.status == MethodNotSupported.status_code

    location = "/update"  # PATCH
    _, response = sanic_server.app.test_client.patch(location)
    assert response.status == ServerError.status_code

    _, response = sanic_server.app.test_client.put(location)
    assert response.status == MethodNotSupported.status_code

    location = "/delete"  # DELETE
    _, response = sanic_server.app.test_client.delete(location)
    assert response.status == ServerError.status_code

    _, response = sanic_server.app.test_client.post(location)
    assert response.status == MethodNotSupported.status_code

    location = "/logout"  # DELETE
    _, response = sanic_server.app.test_client.delete(location)
    assert response.status == ServerError.status_code

    _, response = sanic_server.app.test_client.post(location)
    assert response.status == MethodNotSupported.status_code


def test_user_registration(sanic_server):
    location = "/register"
    attributes = {
        "username": "Some User",
        "email": "definitely_a_real_email_address@fakeho.st",
        "password": "!!!"
    }

    _, response = sanic_server.app.test_client.post(
        location,
        data=ujson.dumps(attributes)
    )

    assert response.status == 200
    assert isinstance(response.json["user_id"], str)
