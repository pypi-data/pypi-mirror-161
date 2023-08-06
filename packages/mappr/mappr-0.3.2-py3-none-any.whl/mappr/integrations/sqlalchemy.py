from typing import Type

from mappr import types
from mappr.iterators import field_iterator


@field_iterator(test=lambda cls: hasattr(cls, '__table__'))
def sa_model_iter_fields(model_cls: Type) -> types.FieldIterator:
    yield from model_cls.__table__.columns.keys()
