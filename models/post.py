import datetime
import orm
from db import database, metadata
from .thread import Thread


class Post(orm.Model):
    __tablename__ = 'posts'
    __database__ = database
    __metadata__ = metadata

    id = orm.Integer(primary_key=True)
    thread = orm.ForeignKey(Thread)
    offset = orm.Integer()
    markdown = orm.Text()
    datetime = orm.DateTime(default=datetime.datetime.now)
