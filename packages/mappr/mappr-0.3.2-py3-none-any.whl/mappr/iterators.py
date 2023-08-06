import dataclasses
from contextvars import ContextVar
from typing import Any, Callable, List, Optional, Type

from . import exc, types


FieldIterList = List[types.FieldIter]
g_field_iterators: ContextVar[FieldIterList] = ContextVar('g_field_iterators', default=[])


def field_iterator(test=types.TestFn):
    def decorator(fn: Callable[[Any], types.FieldIterator]):
        field_iterators = g_field_iterators.get()
        field_iterators.append(types.FieldIter(test=test, iter_factory=fn))
        return fn

    return decorator


def iter_fields(any_cls: Type):
    field_iter = _find_field_iter(any_cls)
    if field_iter:
        yield from field_iter.make_iterator(any_cls)
    else:
        raise exc.TypeNotSupported(any_cls)


def _find_field_iter(any_cls: Type) -> Optional[types.FieldIter]:
    field_iterators = g_field_iterators.get()
    return next(
        (x for x in field_iterators if x.can_handle(any_cls)),
        None
    )


@field_iterator(test=lambda cls: dataclasses.is_dataclass(cls))
def dataclass_iter_fields(model_cls: Type) -> types.FieldIterator:
    yield from (f.name for f in dataclasses.fields(model_cls))
