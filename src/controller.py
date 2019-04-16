from functools import wraps
import logging
import uuid

from email_validator import validate_email
from passlib.context import CryptContext
from sanic.exceptions import NotFound, Unauthorized

from models import Prefixes

# TYPE HINTING #
import typing
from sanic import request
#

pwd_context = CryptContext(schemes=("argon2",))
db = None


async def check_auth(req: request) -> typing.Tuple[str, str]:
    session_id = req.headers["session_id"]
    user_id = await db.get("{}:{}:{}".format(Prefixes.session_id, session_id, Prefixes.user_id))
    return user_id, session_id


def authorised():
    def decorator(f):
        @wraps(f)
        async def decorated_function(request, *args, **kwargs):
            try:
                user_id, session_id = await check_auth(request)
                kwargs["user_id"] = user_id
                kwargs["session_id"] = session_id
                response = await f(request, *args, **kwargs)
                return response
            except AssertionError:
                raise Unauthorized("Must be logged in.")
        return decorated_function
    return decorator


async def new_user(username: str, email: str, password: str) -> str:
    user_id = uuid.uuid4().hex
    p = db.multi_exec()
    p.set("{}:{}".format(username, Prefixes.user_id), user_id)
    p.set("{}:{}".format(user_id, Prefixes.username), username)
    p.set("{}:{}".format(user_id, Prefixes.email), email)
    p.set("{}:{}".format(user_id, Prefixes.password), await process_password(password))
    result = await p.execute()
    if not all(result):
        raise Exception(result)
    return user_id


async def find_user_by_user_id(user_id: str) -> str:
    result = await db.get("{}:{}".format(user_id, Prefixes.username))
    return result


async def find_user_by_username(username: str) -> str:
    result = await db.get("{}:{}".format(username, Prefixes.user_id))
    return result


async def process_password(password: str) -> str:
    return pwd_context.hash(bytes(password, encoding="utf-8"))


async def check_password(user_id: str, password: str) -> bool:
    hash_string = await db.get("{}:{}".format(user_id, Prefixes.password))
    return pwd_context.verify(
        bytes(password, encoding="utf-8"),
        bytes(hash_string, encoding="utf-8")
    )


async def login_user(user_id: str, password: str) -> str:
    username = await find_user_by_user_id(user_id)
    password = await check_password(user_id, password)
    if username is None:
        raise NotFound()

    if not password:
        raise Unauthorized("Invalid password.")

    session_id = uuid.uuid5(
        uuid.UUID(version=4, hex=user_id),
        username
    ).hex
    p = db.multi_exec()
    p.set("{}:{}".format(user_id, Prefixes.session_id), session_id)
    p.set("{}:{}:{}".format(Prefixes.session_id, session_id, Prefixes.user_id), user_id)
    await p.execute()
    return session_id


async def register_account(username: str, email: str, password: str) -> str:
    logging.info(
        "{}, {}, {}".format(username, email, password)  # TODO: REMOVE PASSWORD
    )

    user_id = await find_user_by_username(username)
    validate_email(email, check_deliverability=False)
    if user_id:
        return user_id

    return await new_user(
        username=username,
        email=email,
        password=password
    )


@authorised()
async def logout(*args: tuple, **kwargs: dict) -> None:
    session_id, user_id = kwargs["session_id"], kwargs["user_id"]
    p = db.multi_exec()
    p.delete("{}:{}".format(user_id, Prefixes.session_id))  # logout
    p.delete("{}:{}:{}".format(Prefixes.session_id, session_id, Prefixes.user_id))  # logout
    await p.execute()


@authorised()
async def delete_user(*args: tuple, **kwargs: dict) -> None:
    session_id, user_id = kwargs["session_id"], kwargs["user_id"]

    p = db.multi_exec()
    username = p.get("{}:{}".format(user_id, Prefixes.username))
    p.delete("{}:{}".format(user_id, Prefixes.session_id))  # logout
    p.delete("{}:{}:{}".format(Prefixes.session_id, session_id, Prefixes.user_id)) # logout
    p.delete("{}:{}".format(username, Prefixes.user_id))
    p.delete("{}:{}".format(user_id, Prefixes.username))
    p.delete("{}:{}".format(user_id, Prefixes.email))
    p.delete("{}:{}".format(user_id, Prefixes.password))
    await p.execute()


@authorised()
async def update_user(req: request, *args: tuple, **kwargs: dict) -> typing.Dict[str, str]:
    user_id = kwargs["user_id"]
    attrs_to_update = set(dir(Prefixes)).intersection(req.json)
    try:
        attrs_to_update.remove(Prefixes.session_id)
    except KeyError:
        pass

    p = db.multi_exec()
    if Prefixes.username in attrs_to_update:
        username = p.get("{}:{}".format(Prefixes.user_id, Prefixes.user_id), user_id)
        p.set("{}:{}".format(username, Prefixes.user_id), user_id)

    for attr in attrs_to_update:
        attr_val = Prefixes.__dict__[attr]
        p.set("{}:{}".format(user_id, attr_val), req.json[attr])
    await p.execute()
    return await get_user(request, *args, **kwargs)


@authorised()
async def get_user(req: request, *args: tuple, **kwargs: dict) -> typing.Dict[str, str]:
    user_id = kwargs["user_id"]
    p = db.multi_exec()
    p.get("{}:{}".format(user_id, Prefixes.username))
    p.get("{}:{}".format(user_id, Prefixes.email))
    p.get("{}:{}".format(user_id, Prefixes.password))
    username, email, password = await p.execute()
    return {
        "user_id": user_id,
        "username": username,
        "email": email,
        "password": password
    }
