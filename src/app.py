import aioredis
import logging

from sanic import Sanic, response

import config
import controller

# TYPE HINTING #
from sanic import request
#

app = Sanic(__name__)


@app.listener("before_server_start")
async def server_init(application, _):
    logging.basicConfig(level=config.LOG_LEVEL)
    application.redis = await aioredis.create_redis(
        "redis://{}:{}".format(application.config.DB_HOST, application.config.DB_PORT),
        encoding="utf-8"
    )
    controller.db = application.redis
    return application


@app.route("/register", methods=["POST"])
async def register(req: request) -> response.HTTPResponse:
    user_id = await controller.register_account(
        req.json["username"],
        req.json["email"],
        req.json["password"]
    )
    return response.json(
        body={
            "user_id": user_id
        }
    )


@app.route("/login", methods=["PUT"])
async def login(req: request) -> response.HTTPResponse:
    return response.json(
        body={
            "session_id": await controller.login_user(req.json["user_id"], req.json["password"])
        }
    )


@app.route("/update", methods=["PATCH"])
async def update(req: request) -> response.HTTPResponse:
    return response.json(
        body=await controller.update_user(req)
    )


@app.route("/delete", methods=["DELETE"])
async def delete(req: request) -> response.HTTPResponse:
    await controller.delete_user(req)
    return response.json(
        body={
            "msg": "deleted"
        }
    )


@app.route("/logout", methods=["DELETE"])
async def logout(req: request) -> response.HTTPResponse:
    await controller.logout(req)
    return response.json(
        body={
            "msg": "logged out"
        }
    )


if __name__ == "__main__":
    app.config.DB_HOST = config.DB_HOST
    app.config.DB_PORT = config.DB_PORT
    app.run(host="0.0.0.0", port=9443)
