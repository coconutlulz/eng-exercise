import asyncio
import uuid

import aioredis

from sanic import Sanic, response
from sanic.exceptions import Unauthorized

import config
import models
from controller import login_user, register_account

app = Sanic(__name__)

# GET - get
# POST - create
# PUT - replace or create
# PATCH - update
# DELETE


@app.listener("before_server_start")
async def server_init(app, _):
    app.redis = await aioredis.create_redis("redis://127.0.0.1", encoding="utf-8")
    models.initialise(app.redis)


@app.route("/")
async def test(request):
    return json({
        "hello": "world"
    })


@app.route("/register", methods=["POST"])
async def register(request):
    await register_account(request.username, request.email, request.password)
    return json(
        {"msg": "Registered."}
    )


@app.route("/login", methods=["POST", "PUT"])
async def login(request):
    return response.json(
        body={
            "response": await login_user(request.json["username"], request.json["password"])
        }
    )


if __name__ == "__main__":
    app.config.DB_HOST = config.DB_HOST
    app.config.DB_PORT = config.DB_PORT
    app.run(host="0.0.0.0", port=9443)
