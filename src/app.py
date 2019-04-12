from sanic import Sanic
from sanic.response import json

from . import config
from .controller import login_user, register_account

app = Sanic()

# GET - get
# POST - create
# PUT - replace or create
# PATCH - update
# DELETE


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


@app.route("/login", methods=["POST"])
async def login(request):
    await login_user(request.username, request.password)


if __name__ == "__main__":
    app.config.DB_HOST = config.DB_HOST
    app.config.DB_PORT = config.DB_PORT
    app.run(host="0.0.0.0", port=9443)
