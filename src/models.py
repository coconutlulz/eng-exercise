from astra import models

db = None


def initialise(redis):
    global db
    db = redis


class User(models.Model):
    def get_db(self):
        return db

    user_id = models.IntegerField()
    name = models.CharHash()
    email = models.CharHash()


class Session(models.Model):
    def get_db(self):
        return db

    session_id = models.IntegerField()
    user = models.ForeignKey(to=User)
