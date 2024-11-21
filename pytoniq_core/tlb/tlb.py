from ..boc.deserialize import NullCell
from ..boc.address import Address
from abc import ABC, abstractmethod


def is_builtin_class_instance(obj):
    return obj.__class__.__module__ in ['__builtins__', 'builtins']


class TlbError(Exception):
    pass


class TlbScheme(ABC):
    """
    abstract class for Tlb Schemes wrappers
    """
    @abstractmethod
    def serialize(self, *args): ...

    @classmethod
    @abstractmethod
    def deserialize(cls, *args): ...

    def __repr__(self, t=1):
        # s = f'< Tl-B {self.__class__.__name__} \n'
        # for k, v in self.__dict__.items():
        #     if isinstance(v, (int, str, float, bytes, bool, dict, tuple, list, NullCell, Address, type(None))):
        #         s += '\t' * t + k + ': ' + v.__repr__() + '\n'
        #     else:
        #         s += '\t' * t + k + ': ' + v.__repr__(t + 1) + '\n'
        # return s + '\t' * t + '>' + '\n'
        return f'< Tl-B {self.__class__.__name__} {" ".join([i + ": " + j.__repr__() for i, j in self.__dict__.items()])} >'
        # TODO beautiful repr

    def __json__(self):
        # if __json__ is not defined for a class, it will return str(obj)
        ret = {}
        for i, j in self.__dict__.items():
            if is_builtin_class_instance(j):
                ret[i] = j
            elif hasattr(j, '__json__'):
                ret[i] = j.__json__()
            else:
                ret[i] = str(j)
        ret['type'] = self.__class__.__name__
        return ret
