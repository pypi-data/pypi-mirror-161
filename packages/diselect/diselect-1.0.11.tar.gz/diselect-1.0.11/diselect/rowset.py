from itertools import groupby
from dataclasses import dataclass
from operator import attrgetter
from typing import Callable, List

from .utils import apply_to_depth



@dataclass
class RowItem:
    index: tuple
    alias: str
    applies: List[Callable]
    value: object
    nested_depth: int
    queries_length: int
    matched_pos: int

    @classmethod
    def merge_item(cls, items):
        template, *_ = items
        values = [row.value for row in items]
        kwargs = {**template.__dict__, 'value': values}
        return cls(**kwargs)
    

    def _reduce(self, app, value, depth=0):
        def _join(iterable, sep=app):
            return sep.join(filter(None, iterable))

        function_for_iterable =  [
            sum, min, max, len, all, any,
            list, tuple, set,
            _join, 
        ]
        
        if isinstance(app, str):
            app = _join
        elif app.__name__ == 'join':
            function_for_iterable.append(app)

        if app in function_for_iterable:
            depth = 1

        return apply_to_depth(depth, app, value)

    def apply_values(self, none):
        if self.value is None:
            if none == 'ignore':
                return self
            elif none == 'drop':
                return
            elif none == 'apply':
                pass
            else:
                raise ValueError('none parameter must be in ignore, dorp, apply')
        for app in self.applies:
            self.value = self._reduce(app, self.value)
        return self
    


class RowSet:

    def __init__(self, rowset):
        self.rowset = rowset
        self._merge_multiquery()
        self._compose_deep_value()

    def _merge_multiquery(self):
        result = []
        rowset = sorted(self.rowset, key=attrgetter('queries_length', 'alias', 'index', 'matched_pos'))
        for (length, *_), grouped in groupby(rowset, key=attrgetter('queries_length', 'alias', 'index')):
            if length > 1:
                item = RowItem.merge_item(list(grouped))
                result.append(item)
            else:
                result += list(grouped)
        self.rowset = result
    
    def _compose_deep_value(self):
        result = []
        rowset = sorted(self.rowset, key=attrgetter('alias', 'nested_depth'))
        top_depth = min(r.nested_depth for r in rowset)
        for (_, depth), grouped in groupby(rowset, key=attrgetter('alias', 'nested_depth')):
            if depth > top_depth:
                item = RowItem.merge_item(list(grouped))
                result.append(item)
            else:
                result += list(grouped)
        self.rowset = result
    
    def excute_apply(self, none):
        applied = [
            item.apply_values(none)
            for item in self.rowset
        ]
        self.rowset = list(filter(None, applied))

    def as_values(self, fields=None):
        values = {
            item.alias: item.value for item in self.rowset
        }
        if fields:
            values = {
                f:values[f] for f in fields if f in values
            }
        return values

    def as_result(self, none, fields):
        self.excute_apply(none)
        values = self.as_values(fields)
        return values

        

def produce_rowset(selected, pivot_index):
    groupkey = lambda sel: sel.index[:pivot_index]
    selected = sorted(selected, key=groupkey)
    for _, selected_set in groupby(selected, key=groupkey):
        rows = [
            RowItem(
                s.index, s.alias, s.applies, s.value,
                len(s.index), len(s.queries), s.get_matched_pos()
            )
            for s in selected_set
        ]
        yield RowSet(rows)
