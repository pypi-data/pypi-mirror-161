import inspect
from itertools import takewhile
from collections import abc

from .regex import strcompile
from .exceptions import ReduceModuleException



def find_function(module, regex):
    if not inspect.ismodule(module):
        raise ValueError(f"{module} is Not python module  .py")
    for name, func in inspect.getmembers(module, inspect.isfunction):
        if g := strcompile(regex).search(name):
            yield g.group, func


def module2dict(module):
    return dict(takewhile(lambda i: i[0] != '__builtins__', inspect.getmembers(module)))


def reduce_module2dict(module):
    if inspect.ismodule(module):
        return module2dict(module)
    elif isinstance(module, abc.Mapping):
        return module
    else:
        raise ReduceModuleException(
            f"{module} is must be module or mapping"
        )


def get_kwargnames(callable):
    sig = inspect.signature(callable)
    return list(sig.parameters)


def select_kwargs(callable, *args, allowed_params:list=None, **kwargs):
    allowed_params = allowed_params or []
    allowed_params += get_kwargnames(callable)
    kwargs = {
        key: value for key, value in kwargs.items()
        if key in allowed_params
    }
    return callable(*args, **kwargs)

