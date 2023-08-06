from typing import Any

from . import types


def alias(aliased_name: str) -> types.MappingFn:
    def mapper(o: Any) -> Any:
        return getattr(o, aliased_name, None)
    return mapper


def set_const(value: Any) -> types.MappingFn:
    """ Always set the field to the given value during conversion.

    You can use `mappr.set_const` if you want to set an attribute to a constant
    value during conversion, without concern about the source object. Every
    call to `mappr.convert` will return the same *value*.

    Args:
        value:  The value to set on the field. Instead of using the source
                object attribute or target type field default, this value
                will be set on the field during conversion.

    Returns:
        A mapping function.

    Example:

        >>> from dataclasses import dataclass
        >>> import mappr
        >>>
        >>> @dataclass
        ... class Src:
        ...     text: str = 'hello'
        ...     num: int = 10
        >>>
        >>> @dataclass
        ... class Dst:
        ...     text: str
        ...     num: int = 20
        >>>
        >>> mappr.register(Src, Dst, mapping=dict(
        ...     num=mappr.set_const(100)
        ... ))
        >>>
        >>> src = Src()
        >>> dst = mappr.convert(Dst, src)
        >>>
        >>> dst.text
        'hello'
        >>> dst.num
        100
    """
    def mapper(o: Any) -> Any:
        return value
    return mapper


def use_default(o: Any) -> Any:
    """ Indicate we want to use default field value  rather than value from source object

    Args:
        src_obj:    The converted object. Not used here, but part of the mappers
                    interface so has to be defined.
        name: l     Name of the converted field. Not used here, but part of the
                    mappers interface.

    Returns:
        A mapping function for the field. This is just a stub, as `mappr.convert`
        will just skip the field if it's mapper is set to `mappr.use_default`.

    By default, if the attribute exists on the source object, it's value will be
    used when creating the result. That happens even if the destination type
    defines a default value for that field. If you want to use the default
    provided by the target type you can achive that with `mappr.use_default`
    mapper.
    You simply set the field to `mappr.use_default` and the attribute value
    from the source object won't be used (the target default is used). If the
    target type does not define a default value an exception will be raised
    during the creation of the final result.

    Example:

        >>> from dataclasses import dataclass
        >>> import mappr
        >>>
        >>> @dataclass
        ... class Src:
        ...     text: str = 'hello'
        ...     num: int = 10
        >>>
        >>> @dataclass
        ... class Dst:
        ...     text: str
        ...     num: int = 20
        >>>
        >>> mappr.register(Src, Dst, mapping=dict(
        ...     num=mappr.use_default
        ... ))
        >>>
        >>> src = Src()
        >>> dst = mappr.convert(Dst, src)
        >>>
        >>> dst.text
        'hello'
        >>> dst.num
        20
    """
    return lambda src_obj, name: None   # nocov
