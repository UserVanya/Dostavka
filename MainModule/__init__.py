from telegram import Update
from functools import wraps
class AutoNumberMeta(type):
    _counter = 0
    def __new__(cls, name, bases, attrs):
        for attr_name in attrs.keys():
            if not attr_name.startswith("__"): 
                attrs[attr_name] = cls._counter
                cls._counter += 1
        return super(AutoNumberMeta, cls).__new__(cls, name, bases, attrs)

class AutoNumbered(metaclass=AutoNumberMeta):
    pass
