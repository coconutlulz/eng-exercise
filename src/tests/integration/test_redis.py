import logging

import aioredis

import pytest

from src import config, controller, models
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
    app.redis.flushdb()
    controller.set_db(app.redis)
    return loop.run_until_complete(test_server(app))
