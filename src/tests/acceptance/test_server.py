import logging

import aioredis
import pytest
from sanic.exceptions import Forbidden, MethodNotSupported, ServerError
import ujson

import config
import controller
from app import app as test_app

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
    controller.set_db(app.redis)
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


def _register(server):
    location = "/register"
    username = "Some User"
    email = "definitely_a_real_email_address@fakeho.st"
    password = "!!!ġ"

    attributes = {
        "username": username,
        "email": email,
        "password": password
    }

    _, response = server.app.test_client.post(
        location,
        data=ujson.dumps(attributes)
    )

    assert response.status == 200
    user_id = response.json["user_id"]
    assert isinstance(user_id, str)
    return user_id, password


def _login(server, user_id, password):
    location = "/login"
    attributes = {
        "user_id": user_id,
        "password": password
    }

    _, response = server.app.test_client.put(
        location,
        data=ujson.dumps(attributes)
    )

    return response


def _delete(server, session_id):
    location = "/delete"

    headers = {
        "session_id": session_id
    }

    _, response = server.app.test_client.delete(
        location,
        headers=headers
    )
    assert response.status == 200
    return response


def test_full_flow(sanic_server):
    user_id, password = _register(sanic_server)

    response = _login(sanic_server, user_id, password)
    assert response.status == 200
    session_id = response.json["session_id"]
    assert isinstance(session_id, str)

    _delete(sanic_server, session_id)

    response = _login(sanic_server, user_id, password)
    assert response.status == Forbidden.status_code
