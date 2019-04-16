from functools import wraps
import logging
import uuid

from email_validator import validate_email
from passlib.context import CryptContext
from sanic.exceptions import InvalidUsage, Forbidden, Unauthorized

from models import Prefixes, RedisKeys

# TYPE HINTING #
import typing
from sanic import request
#

pwd_context = CryptContext(schemes=("argon2",))
db = None


def set_db(redis):
    global db
    db = redis


async def check_auth(req: request) -> typing.Tuple[str, str]:
    session_id = req.headers["session_id"]
    logging.info("Checking auth for session_id: {}".format(session_id))

    user_id = await db.get(RedisKeys.session_user_id(session_id))
    logging.info("Got user_id: {}, session_id: {}".format(user_id, session_id))

    if user_id is None:
        raise Unauthorized("Must be logged in.")
    return user_id, session_id


def authorised():
    def decorator(f):
        @wraps(f)
        async def decorated_function(request, *args, **kwargs):
            user_id, session_id = await check_auth(request)
            kwargs["user_id"] = user_id
            kwargs["session_id"] = session_id
            response = await f(request, *args, **kwargs)
            return response
        return decorated_function
    return decorator


async def new_user(username: str, email: str, password: str) -> str:
    hashed_pw = await process_password(password)
    user_id = uuid.uuid4().hex
    p = db.multi_exec()

    p.set(RedisKeys.username(user_id), username)
    p.set(RedisKeys.username_user_id(username), user_id)
    p.set(RedisKeys.email(user_id), email)
    p.set(RedisKeys.password(user_id), hashed_pw)

    result = await p.execute()

    logging.debug("Result for new user creation: {}".format(result))

    if not all(result):
        raise Exception("Failed to create a new user.")

    return user_id


async def find_user_by_user_id(user_id: str) -> str:
    return await db.get(RedisKeys.username(user_id))


async def find_user_by_username(username: str) -> str:
    return await db.get(RedisKeys.username_user_id(username))


async def process_password(password: str) -> str:
    return pwd_context.hash(bytes(password, encoding="utf-8"))


async def _check_password(hash_string: str, password: str) -> bool:
    pw_hash = bytes(password, encoding="utf-8")

    return pwd_context.verify(
        pw_hash,
        bytes(hash_string, encoding="utf-8")
    )


async def check_password(user_id: str, password: str) -> bool:
    hash_string = await db.get(RedisKeys.password(user_id))
    return await _check_password(hash_string, password)


async def login_user(user_id: str, password: str) -> str:
    username = await find_user_by_user_id(user_id)

    if username is None:
        raise Forbidden("This user does not exist.")

    password = await check_password(user_id, password)

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
        raise InvalidUsage("Username already exists.")

    return await new_user(
        username=username,
        email=email,
        password=password
    )


@authorised()
async def logout(*args: tuple, **kwargs: dict) -> None:
    session_id, user_id = kwargs["session_id"], kwargs["user_id"]
    p = db.multi_exec()
    p.unlink(RedisKeys.session_id(user_id), RedisKeys.session_user_id(session_id))
    await p.execute()


@authorised()
async def delete_user(*args: tuple, **kwargs: dict) -> None:
    session_id, user_id = kwargs["session_id"], kwargs["user_id"]

    p = db.multi_exec()

    username = p.get(RedisKeys.username(user_id))
    p.unlink(
        RedisKeys.session_id(user_id),
        RedisKeys.session_user_id(session_id),
        RedisKeys.username_user_id(username),
        RedisKeys.username(user_id),
        RedisKeys.email(user_id),
        RedisKeys.password(user_id)
    )

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
        username = p.get(RedisKeys.username(user_id))
        p.set(RedisKeys.username_user_id(username), user_id)

    for attr in attrs_to_update:
        attr_val = Prefixes.lookup(attr)
        p.set("{}:{}".format(user_id, attr_val), req.json[attr])

    await p.execute()

    return await get_user(req, *args, **kwargs)


@authorised()
async def get_user(req: request, *args: tuple, **kwargs: dict) -> typing.Dict[str, str]:
    user_id = kwargs["user_id"]

    p = db.multi_exec()

    p.get(RedisKeys.username(user_id))
    p.get(RedisKeys.email(user_id))
    p.get(RedisKeys.password(user_id))

    username, email, password = await p.execute()

    return {
        "user_id": user_id,
        "username": username,
        "email": email,
        "password": password
    }
