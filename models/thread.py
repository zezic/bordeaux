import itertools
import string
import random
import orm
from db import database, metadata
from .board import Board


THREAD_SLUG_CHARS = set(string.digits + string.ascii_lowercase)
ALL_THREAD_SLUGS = set(''.join(x) for x in itertools.product(
    set(THREAD_SLUG_CHARS), repeat=4
))

class Thread(orm.Model):
    __tablename__ = 'threads'
    __database__ = database
    __metadata__ = metadata

    id = orm.Integer(primary_key=True)
    slug = orm.String(index=True, unique=True, min_length=4, max_length=4)
    board = orm.ForeignKey(Board)


class ThreadSlugGenerator():
    def __init__(self):
        self.free_slugs = []

    def register_threads(self, threads):
        self.taken_slugs = [str(thread.slug) for thread in threads]
        self.free_slugs = list(ALL_THREAD_SLUGS - set(self.taken_slugs))

    def get(self):
        return self.free_slugs.pop(random.randrange(len(self.free_slugs)))

    def put(self, freed_slug):
        self.free_slugs.append(freed_slug)
