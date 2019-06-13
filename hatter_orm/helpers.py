import collections
import logging
import sqlite3
from functools import wraps


class OrderedClass(type):
    @classmethod
    def __prepare__(mcs, name, bases):
        return collections.OrderedDict()

    def __new__(mcs, name, base_class, class_dict):
        class_dict['__dict_ordered__'] = [key for key in class_dict.keys() if key not in ('__module__', '__qualname__')]
        return type.__new__(mcs, name, base_class, class_dict)


def try_or_error(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except (sqlite3.OperationalError, TypeError) as e:
            logging.error(e)
            print(f.__name__, e)
            return None
    return wrap
