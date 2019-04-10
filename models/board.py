import orm
from db import database, metadata


class Board(orm.Model):
    __tablename__ = 'boards'
    __database__ = database
    __metadata__ = metadata

    id = orm.Integer(primary_key=True)
    slug = orm.String(index=True, unique=True, max_length=4)
    title = orm.String(unique=True, max_length=24)
