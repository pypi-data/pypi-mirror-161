import collections
from collections import abc


def ist(C):
    def f(x):
        f.__name__ = "isinstance_of_%s" % C.__name__
        if not isinstance(x, C):
            raise ValueError("Value is not an instance of %s." % C.__name__)

    return f


def m_new_contract(name, f):
    from contracts.library.extensions import CheckCallable
    from contracts.library.extensions import Extension

    Extension.registrar[name] = CheckCallable(f)


m_new_contract("Container", ist(abc.Container))
# todo: Iterable(x)
m_new_contract("Iterable", ist(abc.Iterable))

m_new_contract("Hashable", ist(abc.Hashable))


m_new_contract("Iterator", ist(abc.Iterator))
m_new_contract("Sized", ist(abc.Sized))
m_new_contract("Callable", ist(abc.Callable))
m_new_contract("Sequence", ist(abc.Sequence))
m_new_contract("Set", ist(abc.Set))
m_new_contract("MutableSequence", ist(abc.MutableSequence))
m_new_contract("MutableSet", ist(abc.MutableSet))
m_new_contract("Mapping", ist(abc.Mapping))
m_new_contract("MutableMapping", ist(abc.MutableMapping))
# new_contract('MappingView', ist(collections.MappingView))
# new_contract('ItemsView', ist(collections.ItemsView))
# new_contract('ValuesView', ist(collections.ValuesView))


# Not a lambda to have better messages
def is_None(x):
    return x is None


m_new_contract("None", is_None)
m_new_contract("NoneType", is_None)
