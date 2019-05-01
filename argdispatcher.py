# coding: utf-8
"""
Doctests & examples

>>> class ForKey:
...
...     @dispatcher(key='key', value='value-1')
...     def cases(self, first, *args, **kwargs):
...         " On first[key] == `value-1` call this method "
...         return first['marker'] == 'value-1', args, kwargs
...
...     @cases.match(value='value-2')
...     def _(self, first, *args, **kwargs):
...         " On first[key] == `value-2` call this method "
...         return first['marker'] == 'value-2', args, kwargs
...
...     @cases.match(value='value-3')
...     def _(self, first, *args, **kwargs):
...         " On first[key] == `value-3` call this method "
...         return first['marker'] == 'value-3', args, kwargs
...
...     @cases.nomatch
...     def _(self, first, *args, **kwargs):
...         " Call this method if passed value has no match "
...         return False, first, args, kwargs

>>> import collections
>>> Data = collections.namedtuple('Data', 'attr marker')

>>> class ForAttr:
...
...     @dispatcher(attr='attr', value='value-1')
...     def cases(self, first, *args, **kwargs):
...         return first.marker == 'value-1', args, kwargs
...
...     @cases.match(value='value-2')
...     def _(self, first, *args, **kwargs):
...         " On first[key] == `value-2` call this method "
...         return first.marker == 'value-2', args, kwargs
...
...     @cases.match(value='value-3')
...     def _(self, first, *args, **kwargs):
...         " On first[key] == `value-3` call this method "
...         return first.marker == 'value-3', args, kwargs

>>> fk = ForKey()
>>> fk.cases({'key': 'value-1', 'marker': 'value-1'}, 'args1', kwargs1=True) == (True, ('args1',), {'kwargs1': True})
True
>>> fk.cases({'key': 'value-2', 'marker': 'value-2'}, 'args2', kwargs2=True) == (True, ('args2',), {'kwargs2': True})
True
>>> fk.cases({'key': 'value-3', 'marker': 'value-3'}, 'args3', kwargs3=True) == (True, ('args3',), {'kwargs3': True})
True
>>> fk.cases({'key': 'value-4', 'marker': 'value-4'}, 'args4', kwargs4=True) == (False, {'marker': 'value-4', 'key': 'value-4'}, ('args4',), {'kwargs4': True})
True

>>> fa = ForAttr()
>>> fa.cases(Data(attr='value-1', marker='value-1')) == (True, (), {})
True
>>> fa.cases(Data(attr='value-2', marker='value-2')) == (True, (), {})
True
>>> fa.cases(Data(attr='value-3', marker='value-3')) == (True, (), {})
True

no first argument provided
>>> fa.cases()
Traceback (most recent call last):
TypeError: Dispatcher expect at least one positional argument for matching

no matching key
>>> fk.cases({'value': 'tests'})
Traceback (most recent call last):
ValueError: First argument doesn't contains key "key"

no match case provided
>>> fa.cases(Data(attr='value-4', marker='value-4'))
Traceback (most recent call last):
TypeError: Handler for "value-4" is not registered
"""
import operator


_NOMATCH = object()


class Dispatcher:

    def __init__(self, key, value, handler, getter, contains):
        """ Setup params & getters """
        self._key = key
        self._mapping = {}
        self._getter = getter
        self._contains = contains
        self._set_link(value, handler)

    def __get__(self, instance, instance_type):
        """ Check passed parameters & dispatch call """
        def wrapper(*args, **kwargs):
            # first argument passed?
            try:
                first = args[0]
            except IndexError:
                raise TypeError(f'{type(self).__name__} expect at least one positional argument for matching')
            # key in passed argument?
            if not self._contains(first, self._key):
                raise ValueError(f'First argument doesn\'t contains key "{self._key}"')
            # get value, check if it's in mapping, if "nomatch" case provided -> return default
            value = self._getter(first)
            if value not in self._mapping:
                if _NOMATCH not in self._mapping:
                    raise TypeError(f'Handler for "{value}" is not registered')
                value = _NOMATCH
            # all checks passed, dispatch call by value
            return self._mapping[value](instance, first, *args[1:], **kwargs)
        return wrapper

    def _set_link(self, value, handler):
        """ Link value to handler """
        self._mapping[value] = handler

    def match(self, value):
        """ Add case-handlers """
        def wrapper(method):
            if value in self._mapping:
                raise TypeError(f'Handler for "{value}" already registered')
            self._set_link(value, method)
            return self
        return wrapper

    def nomatch(self, method):
        """ Add default case-handler """
        self._set_link(_NOMATCH, method)
        return self


def dispatcher(attr=None, key=None, value=None):
    """ Match attr or key of first positional argument to specific implementation """
    def wrapper(method):
        if key:
            return Dispatcher(key, value, method, operator.itemgetter(key), operator.contains)
        if attr:
            return Dispatcher(attr, value, method, operator.attrgetter(attr), hasattr)
        raise ValueError('Provide either "key" or "attr" argument for matching')
    return wrapper


if __name__ == '__main__':
    import doctest
    doctest.testmod()
