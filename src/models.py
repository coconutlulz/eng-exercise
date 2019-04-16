class Prefixes:
    user_id = "uid"
    username = "u"
    email = "e"
    password = "p"
    session_id = "sid"

    @classmethod
    def lookup(cls, key):
        return cls.__dict__[key]
