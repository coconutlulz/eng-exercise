from pynamodb.attributes import (
    UnicodeAttribute, NumberAttribute
)
from pynamodb.indexes import GlobalSecondaryIndex, KeysOnlyProjection
from pynamodb.models import Model


class UserViewIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = 'username'
        projection = KeysOnlyProjection()
    username = UnicodeAttribute(hash_key=True)


class User(Model):
    user_id = NumberAttribute(hash_key=True)
    username = UnicodeAttribute()
    email = UnicodeAttribute()
    password = UnicodeAttribute()

    view_index = UserViewIndex()


class SessionViewIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = 'session_id'
        projection = KeysOnlyProjection()
    session_id = UnicodeAttribute(hash_key=True)


class SessionMapping(Model):
    user_id = NumberAttribute(hash_key=True)
    session_id = UnicodeAttribute()

