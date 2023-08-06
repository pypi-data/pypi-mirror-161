.. readme_badges_start

|circleci| |nbsp| |codecov| |nbsp| |mypy| |nbsp| |license| |nbsp| |py_ver|


.. |circleci| image:: https://circleci.com/gh/novopl/mappr.svg?style=shield
                :target: https://circleci.com/gh/novopl/mappr
.. |codecov| image:: https://codecov.io/gh/novopl/mappr/branch/master/graph/badge.svg?token=SLX4NL21H9
                :target: https://codecov.io/gh/novopl/mappr
.. |mypy| image:: https://img.shields.io/badge/type_checked-mypy-informational.svg
.. |license| image:: https://img.shields.io/badge/License-Apache2-blue.svg
.. |py_ver| image:: https://img.shields.io/badge/python-3.7+-blue.svg
.. |nbsp| unicode:: 0xA0

.. readme_badges_end

#####
mappr
#####


Easily convert between arbitrary types.


Goals
=====

.. readme_about_start

**mappr**'s goal is to make it as easy as possible to define custom converters
between arbitrary types in python. It does not concern itself with validation
or coercion. It only provides a simple way to define a mapping between two
types + some extra functionality to automatically generate converters for simple
cases (off by default).

.. readme_about_end


Links
=====

* `Documentation`_

    * `Contribute`_
    * `Reference`_


.. _Documentation: https://novopl.github.io/mappr
.. _Contribute: https://novopl.github.io/mappr/pages/contrib.html
.. _Reference: https://novopl.github.io/mappr/pages/reference.html


Installation
============

.. readme_installation_start

.. code-block:: shell

    $ pip install mappr

or if you're using poetry.

.. code-block:: shell

    $ poetry add mappr

.. readme_installation_end


If you'd like to setup the project locally for development, see `Contribute`_ for
more details.


Quick Example
=============

See the `Documentation`_ for more examples.

.. readme_example_start

Assume we have a following types in our app. They represent pretty much the same
thing, but different views of it.

.. code-block:: python

    from dataclasses import dataclass
    import mappr


    @dataclass
    class User:
        username: str
        first_name: str
        last_name: str
        email: str


    class Person:
        def __init__(self, nick, name, email):
            self.nick = nick
            self.name = name
            self.email = email


    # Since we're not using any base class supported out of the box by mappr
    # we need to define a field_iterator for our Person class. mappr
    # comes bundled with ones for dataclasses, pydantic (ptional) and
    # SQLAlchemy (optional). field_iterators are very easy to implement so more
    # will follow. Of course you can also use field iterators defined by 3rd
    # party packages. Just needs to be imported prior to converting any objects.
    @mappr.field_iterator(test=lambda target_cls: isinstance(target_cls, Person))
    def iter_person(model_cls: Type) -> mappr.FieldIterator:
        yield from ['nick', 'name', 'email']

    # register User -> Person converter ('email' matches by name so can be skipped)
    mappr.register(User, Person, mapping=dict(
        nick=lambda obj, name: obj.username,
        name=lambda obj, name: f"{obj.first_name} {obj.last_name}",
    ))
    # register Person -> User converter
    mappr.register(User, Person, mapping=dict(
        username=lambda obj, name: obj.nick,
        first_name=lambda obj, name: obj.name and obj.name.split()[0],
        last_name=lambda obj, name: obj.name and obj.name.split()[-1],
    ))

    user = User(
        username='john.doe',
        first_name='John',
        last_name='Doe',
        email='john.doe@example.com',
    )

    person = mappr.convert(Person, user)
    assert person == Person(
        name='John Doe',
        email='john.doe@example.com',
        nick='john.doe',
    )

    user2 = mappr.Convert(User, person)
    assert user2 == user

.. readme_example_end
