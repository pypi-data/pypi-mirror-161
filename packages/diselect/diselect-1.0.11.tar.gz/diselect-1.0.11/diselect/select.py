import logging
from dataclasses import dataclass

from .exceptions import *
from .flatten.item import FlatItem
from .queryset.query import Query


logging.basicConfig(format='diselect %(levelname)s: %(message)s')



@dataclass
class SelectItem(FlatItem, Query):

    def get_matched_parts(self):
        return self.match_path(self.path)

    def get_matched_pos(self):
        matched_parts = self.get_matched_parts()
        return self.queries.index(matched_parts)

    def is_exact_matched(self):
        return self.path in self.queries
    
    def was_exact_matched(self, exact_history):
        return set(self.queries) & set(exact_history)



def produce_selected(flatten, queryset):
    selected = [
        SelectItem(**flat.as_kwargs(), **query.as_kwargs())
        for flat in flatten
        for query in queryset.produce_matched(flat.path)
    ]

    exact_matched_history = set([
       sel.get_matched_parts() for sel in selected
       if sel.is_exact_matched()
    ])

    matchedset = {}    
    validated = []
    for item in selected:
        if item.was_exact_matched(exact_matched_history):
            if not item.is_exact_matched():
                continue
        
        parts = item.get_matched_parts()
        matchedset.setdefault(parts, set()).add(item.path)
        validated.append(item)
    
    for parts, paths in matchedset.items():
        if len(paths) > 1:
            raise QueryMultipleMatched(parts, paths)

    if undermatched:=set(queryset.get_flatten_query()) - matchedset.keys():
        logging.warning(f'Cannot match path with query: {undermatched}')

    return validated


def get_top_depth(selected):
    return min([len(sel.index) for sel in selected], default=0)




