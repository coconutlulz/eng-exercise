import logging

from email_validator import validate_email, EmailNotValidError
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=("argon2",))


async def process_password(username, password):
    pwd_context.hash(password, user=username)

async def check_password(username, password, hash_string):
    pwd_context.verify(password, hash_string, user=username)


async def login_user(username, password):
    pass


async def register_account(username, email, password):
    logging.info(
        "{}, {}, {}".format(username, email, password)  # TODO: REMOVE PASSWORD
    )

    try:
        validate_email(email)
    except EmailNotValidError as e:
        raise e

    # Check user doesn't already exist.
    # Check email doesn't already exist.
