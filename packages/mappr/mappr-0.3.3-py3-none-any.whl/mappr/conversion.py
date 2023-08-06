from typing import Any, Dict, Optional, Type, TypeVar

from . import iterators, mappers, registry
from .enums import Strategy


T = TypeVar('T')


def convert(
    dst_type: Type[T],
    src_obj,
    strict: bool = True,
    strategy: Optional[Strategy] = None,
) -> T:
    """ Convert an object to a given type.

    Args:
        dst_type:   Target type. This is the type of the return value.
        src_obj:    An object to convert. A registered converter will be used
                    to map between the attributes of this object and the target
                    type.
        strict:     If set to ``False`` and the converter is not found for the
                    given type pair, it will create an ad-hoc one that maps
                    the attributes by their name. Defaults to ``True``

    Returns:
        A newly created instance of ``dst_type`` with values initialized
        from ``src_obj``.
    """
    converter = registry.get_converter(src_obj.__class__, dst_type, strict=strict)
    strategy = strategy or converter.strategy
    values = {}

    for name in iterators.iter_fields(dst_type):
        mapping_fn = converter.mapping.get(name, mappers.alias(name))

        if mapping_fn != mappers.use_default:
            values[name] = mapping_fn(src_obj)

    if strategy == Strategy.CONSTRUCTOR:
        return _build_by_constructor(dst_type, values)
    else:
        return _build_by_setattr(dst_type, values)


def _build_by_constructor(dst_type: Type[T], values: Dict[str, Any]) -> T:
    return dst_type(**values)   # type: ignore


def _build_by_setattr(dst_type: Type[T], values: Dict[str, Any]) -> T:
    result = dst_type()
    for name, value in values.items():
        setattr(result, name, value)

    return result
