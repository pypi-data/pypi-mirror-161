from functools import reduce
from typing import List, Callable
from dataclasses import dataclass

from ..utils.bases import ParameterBase
from .normalize import query2dict, multiply_querykey, set_queryvalue



@dataclass
class Query(ParameterBase):
    queries: tuple
    alias: str
    applies: List[Callable]

    def match_path(self, path):
        for parts in self.queries:
            if path[-len(parts):] == parts:
                return parts
    
        
class QuerySet:

    def __init__(self, queryset:List[Query]):
        self.qs = queryset

    def produce_matched(self, path:tuple):
        yield from (
            Query(**query.as_kwargs()) for query in self.qs 
            if query.match_path(path)
        )

    def get_query(self, queries):
        for query in self.qs:
            if query.queries == queries:
                return query

    def get_flatten_query(self):
        return reduce(lambda acc, cur: acc + cur.queries, self.qs, ())

    def get_aliases(self):
        return [
            q.alias for q in self.qs
        ]


def get_queryset(query, _depth=0):
    if _depth == 0:
        query = query2dict(query)
        return get_queryset(query, _depth=_depth+1)
    elif _depth == 1:
        qs = [
            Query(multiply_querykey(key), *set_queryvalue(value))
            for key, value in query.items()
        ]
        return QuerySet(qs)
