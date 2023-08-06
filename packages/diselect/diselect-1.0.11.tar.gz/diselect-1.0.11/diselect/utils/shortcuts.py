def flatten_list(container):
    if isinstance(container, (list, tuple)):
        for value in container:
            yield from flatten_list(value)
    else:
        yield value


def get_nested_depth(nested):
    def counter(nest, count=0):
        if isinstance(nest, (list, tuple)):
            count += 1
            for t in nest:
                yield from counter(t, count)
        yield count
    return max(counter(nested))


def apply_to_depth(depth, func, value):
    cur = get_nested_depth(value)

    if cur <= depth:
        return func(value)

    if isinstance(value, (list, tuple)):
        return [
            apply_to_depth(depth, func, v) for v in value
        ]


def concat(lists, seps, _depth=0):
    r = []
    if seps == '':
        sep = ''
    else:
        idx = min(_depth, len(seps)-1)
        sep = seps[idx]
    
    if all(map(lambda x: isinstance(x, list), lists)):
        for l in lists:
            s = concat(l, seps, _depth=_depth+1)
            r.append(s)
    else:
        return sep.join(filter(None, map(str, lists)))
    return sep.join(filter(None, map(str, r)))

