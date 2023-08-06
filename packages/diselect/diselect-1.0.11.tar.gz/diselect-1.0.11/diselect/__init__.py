from .select import produce_selected, get_top_depth
from .rowset import produce_rowset
from .queryset import get_queryset
from .flatten import flatten_container



def diselect(container, query, none='ignore'):
    ''' - query examples: 
        [field1, field2],
        {
            field1: alias1,
            field2: [alias2, function1, function2, ...],
            field3: [alias2, ','], # join sep
        }
        - useage:
          diselect(data, {('path1,', 'path2): ('alias', int)})
        - parameters
        none -'ignore'(defalut): function appling is ignored for None value
             -'drop': remove column if value is None 
             -'apply': Treated like any other value
    '''
    # prepare data
    flatten = flatten_container(container)
    qs = get_queryset(query)

    # filter data
    selected = produce_selected(flatten, qs)

    # grouping and transform data
    pivot_index = get_top_depth(selected)
    for rowset in produce_rowset(selected, pivot_index):
        yield rowset.as_result(none=none, fields=qs.get_aliases())
