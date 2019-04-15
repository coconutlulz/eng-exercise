from astra import models

db = None


def initialise(redis):
    global db
    db = redis


class Prefixes:
    user_id = "uid"
    username = "u"
    email = "e"
    password = "p"
    session_id = "sid"
