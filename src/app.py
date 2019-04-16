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


@app.route("/user", methods=["GET"])
async def user(req: request) -> response.HTTPResponse:
    """
    GET /user

    Get user information. Requires a session ID.

    Headers:
        - session_id: str

    Returns: None
    """
    user_info = await controller.get_user(req)
    return response.json(user_info)


@app.route("/register", methods=["POST"])
async def register(req: request) -> response.HTTPResponse:
    """
    POST /register

    Register a new account.

    Params:
        - username: str
        - email: str
        - password: str

    Returns:
        - user_id: str
    """
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
    """
    PUT /login

    Log in with a password.

    Params:
        - user_id: str
        - password: str

    Returns:
        - session_id: str
    """
    return response.json(
        body={
            "session_id": await controller.login_user(req.json["user_id"], req.json["password"])
        }
    )


@app.route("/update", methods=["PATCH"])
async def update(req: request) -> response.HTTPResponse:
    """
    PATCH /update

    Update a user's information. Partial data accepted.

    Headers:
        - session_id: str

    Params:
        - username: str (optional)
        - email : str (optional)
        - password: str (optional)

    Returns:
        - user_id: str
        - username: str
        - email: str
        - password: str
    """
    return response.json(
        body=await controller.update_user(req)
    )


@app.route("/delete", methods=["DELETE"])
async def delete(req: request) -> response.HTTPResponse:
    """
    DELETE /delete

    Remove a user's account.

    Headers:
        - session_id: str

    Returns:
        - "deleted": str
    """
    await controller.delete_user(req)
    return response.json(
        body={
            "msg": "deleted"
        }
    )


@app.route("/logout", methods=["DELETE"])
async def logout(req: request) -> response.HTTPResponse:
    """
    DELETE /logout

    Remove the user's current session.

    Headers:
        - session_id: str

    Returns:
        - "logged out": str
    """
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
