from contextvars import ContextVar
from typing import Dict, List, Optional, Type, TypeVar

from . import exc, mappers, types
from .enums import Strategy


T = TypeVar('T')
TypeConverterList = List[types.TypeConverter]
g_converters: ContextVar[TypeConverterList] = ContextVar('g_converters', default=[])


def register(
    src_type: Type,
    dst_type: Type,
    strategy: Strategy = Strategy.CONSTRUCTOR,
    mapping: Optional[types.FieldMapping] = None,
    strict: bool = True
):
    """ Register new converter.

    Args:
        src:
        dst:
        mapping:

    Returns:

    """
    existing = find_converter(src_type, dst_type)
    converters = g_converters.get()

    if existing:
        if strict:
            raise exc.ConverterAlreadyExists(src_type, dst_type)
        else:
            converters.remove(existing)

    converters.append(types.TypeConverter(
        src_type=src_type,
        dst_type=dst_type,
        mapping=mapping or {},
        strategy=strategy,
    ))


def register_iso(
    src_type: Type,
    dst_type: Type,
    strategy: Strategy = Strategy.CONSTRUCTOR,
    mapping: Optional[Dict[str, str]] = None,
    strict: bool = True,
):
    mapping = mapping or {}

    if strict:
        if find_converter(src_type, dst_type):
            raise exc.ConverterAlreadyExists(src_type, dst_type)
        if find_converter(dst_type, src_type):
            raise exc.ConverterAlreadyExists(dst_type, src_type)

    register(src_type, dst_type, strategy=strategy, strict=strict, mapping={
        k: mappers.alias(v) for k, v in mapping.items()
    })
    register(dst_type, src_type, strategy=strategy, strict=strict, mapping={
        v: mappers.alias(k) for k, v in mapping.items()
    })


def get_converter(src_type: Type, dst_type: Type[T], strict: bool) -> types.TypeConverter:
    """ Do everything to return a converter or raise if it's not possible.

    In **strict** mode, it will not create an ad-hoc default converter and will
    require the converter to have been registered earlier.
    """
    converter = find_converter(src_type, dst_type)
    if converter:
        return converter
    elif not strict:
        # If not strict, create an ad-hoc converter for the types. This will try
        # to map the properties from `dst_type` to src_type. `dst_types` attributes
        # must be a subset of `src_type` attributes.
        return types.TypeConverter(src_type=src_type, dst_type=dst_type)
    else:
        raise exc.NoConverter(src_type, dst_type)


def find_converter(src_type, dst_type) -> Optional[types.TypeConverter]:
    converters = g_converters.get()
    return next(
        (c for c in converters if c.src_type == src_type and c.dst_type == dst_type),
        None
    )
