from functools import wraps
import logging
import uuid

from email_validator import validate_email
from passlib.context import CryptContext
from sanic.exceptions import NotFound, Unauthorized

from models import Prefixes

pwd_context = CryptContext(schemes=("argon2",))
db = None


async def check_auth(request):
    user_id = request.json["user_id"]
    session_id = request.headers["session_id"]
    assert session_id == await db.get("{}:{}".format(user_id, Prefixes.session_id))
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


async def new_user(username, email, password):
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


async def find_user(username, user_id=None):
    result = await db.get("{}:{}".format(username, Prefixes.user_id))
    if user_id is not None:
        return user_id
    return result


async def process_password(password):
    return pwd_context.hash(bytes(password, encoding="utf-8"))


async def check_password(user_id, password):
    hash_string = await db.get("{}:{}".format(user_id, Prefixes.password))
    return pwd_context.verify(
        bytes(password, encoding="utf-8"),
        bytes(hash_string, encoding="utf-8")
    )


async def login_user(username, password):
    user_id = await find_user(username)
    if user_id is None:
        raise NotFound()

    password = await check_password(user_id, password)
    if not password:
        raise Unauthorized("Invalid password.")

    session_id = uuid.uuid5(
        uuid.UUID(version=4, hex=user_id),
        username
    ).hex
    await db.set("{}:{}".format(user_id, Prefixes.session_id), session_id)
    return session_id


async def register_account(username, email, password):
    logging.info(
        "{}, {}, {}".format(username, email, password)  # TODO: REMOVE PASSWORD
    )

    user_id = await find_user(username)
    if user_id:
        return user_id

    validate_email(email, check_deliverability=False)

    return await new_user(
        username=username,
        email=email,
        password=password
    )


@authorised()
async def logout(*args, **kwargs):
    session_id, user_id = kwargs["session_id"], kwargs["user_id"]
    db.delete("{}:{}".format(user_id, Prefixes.session_id))  # logout


@authorised()
async def delete_user(*args, **kwargs):
    session_id, user_id = kwargs["session_id"], kwargs["user_id"]

    p = db.multi_exec()
    username = p.get("{}:{}".format(user_id, Prefixes.username))
    p.delete("{}:{}".format(user_id, Prefixes.session_id))  # logout
    p.delete("{}:{}".format(username, Prefixes.user_id))
    p.delete("{}:{}".format(user_id, Prefixes.username))
    p.delete("{}:{}".format(user_id, Prefixes.email))
    p.delete("{}:{}".format(user_id, Prefixes.password))
    await p.execute()
