from dataclasses import dataclass

from ..utils.bases import ParameterBase




@dataclass
class FlatItem(ParameterBase):
    index:tuple
    path: tuple
    value: object



def flatten_container(container, index=None, path=None):
    index = index or (0,)
    path = path or ()

    if not isinstance(container, (dict, list)):
        yield FlatItem(index, path, container)

    if isinstance(container, dict):
        for key, val in container.items():
            yield from flatten_container(val, index, (*path, key))
    elif isinstance(container, (list, tuple, set)):
        for i, val in enumerate(container):
            yield from flatten_container(val, (*index, i), path)