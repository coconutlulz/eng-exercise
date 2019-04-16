class Prefixes:
    user_id = "uid"
    username = "u"
    email = "e"
    password = "p"
    session_id = "sid"

    @classmethod
    def lookup(cls, key):
        return cls.__dict__[key]


class RedisKeys:
    @staticmethod
    def session_id(user_id):
        return "{}:{}".format(user_id, Prefixes.session_id)

    @staticmethod
    def session_user_id(session_id):
        return "{}:{}:{}".format(Prefixes.session_id, session_id, Prefixes.user_id)

    @staticmethod
    def username_user_id(username):
        return "{}:{}".format(username, Prefixes.user_id)

    @staticmethod
    def username(user_id):
        return "{}:{}".format(user_id, Prefixes.username)

    @staticmethod
    def email(user_id):
        return "{}:{}".format(user_id, Prefixes.email)

    @staticmethod
    def password(user_id):
        return "{}:{}".format(user_id, Prefixes.password)
