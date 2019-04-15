import asyncio
import uuid

import aioredis

from sanic import Sanic, response
from sanic.exceptions import Unauthorized

import config
import controller
import models

app = Sanic(__name__)

# GET - get
# POST - create
# PUT - replace or create
# PATCH - update
# DELETE


@app.listener("before_server_start")
async def server_init(app, _):
    app.redis = await aioredis.create_redis("redis://127.0.0.1", encoding="utf-8")
    controller.db = app.redis


@app.route("/register", methods=["POST"])
async def register(request):
    user_id = await controller.register_account(
        request.json["username"],
        request.json["email"],
        request.json["password"]
    )
    return response.json(
        body={
            "user_id": user_id
        }
    )


@app.route("/login", methods=["PUT"])
async def login(request):
    return response.json(
        body={
            "msg": await controller.login_user(request.json["username"], request.json["password"])
        }
    )


@app.route("/delete", methods=["DELETE"])
async def delete(request):
    return response.json(
        body={
            "msg": await controller.delete_user(request)
        }
    )


if __name__ == "__main__":
    app.config.DB_HOST = config.DB_HOST
    app.config.DB_PORT = config.DB_PORT
    app.run(host="0.0.0.0", port=9443)
