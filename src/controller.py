import logging
import uuid

from email_validator import validate_email, EmailNotValidError
from passlib.context import CryptContext
from sanic.exceptions import NotFound

from models import Prefixes

pwd_context = CryptContext(schemes=("argon2",))
db = None


async def new_user(username, email, password):
    user_id = uuid.uuid4().hex
    p = db.multi_exec()
    p.set("{}:{}".format(username, Prefixes.user_id), user_id)
    p.set("{}:{}".format(user_id, Prefixes.username), username)
    p.set("{}:{}".format(user_id, Prefixes.email), email)
    p.set("{}:{}".format(user_id, Prefixes.password), await process_password(password))
    result = await p.execute()
    return False not in result


async def find_user(username, user_id=None):
    result = await db.get("{}:{}".format(username, Prefixes.user_id))
    if user_id is not None:
        return user_id
    return result


async def process_password(password):
    return pwd_context.hash(password)


async def check_password(user_id, password):
    hash_string = await db.get("{}:{}".format(user_id, Prefixes.password))
    x = pwd_context.verify(password, hash_string)
    return


async def login_user(username, password):
    user_id = await find_user(username)
    if user_id is None:
        raise NotFound()

    password = await check_password(user_id, password)

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

    already_exists = await find_user(username)
    if already_exists:
        return True

    try:
        validate_email(email)
    except EmailNotValidError as e:
        raise e

    return await new_user(
        username=username,
        email=email,
        password=await process_password(password)
    )

