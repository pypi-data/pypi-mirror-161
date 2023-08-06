from ..utils import get_nested_depth
from ..exceptions import InvalidQueryKey, InvalidQueryValues



def query2dict(query):
    qs = {}
    if isinstance(query, (list, tuple)):
        for qry in query:
            if isinstance(qry, (str, tuple)):
                qs[qry] = qry
            elif isinstance(qry, dict):
                qs.update(qry)
    elif isinstance(query, dict):
        qs.update(query)
    else:
        raise InvalidQueryKey(query)
    return qs


def multiply_querykey(key):
    query_depth = get_nested_depth(key)
    switch = {
        0: lambda x: ((x,),),
        1: lambda x: (x,),
        2: lambda x: x
    }
    if trans:= switch.get(query_depth):
        return trans(key)
    else:
        raise ValueError('Too many tuple nesting:{}'.format(key))


def set_queryvalue(value):
    alias, apply = None, [lambda x:x]
    if isinstance(value, str):
        alias = value
    elif isinstance(value, (tuple, list)):
        alias, *apply = value
    else:
        raise InvalidQueryValues(value)
    return alias, apply


