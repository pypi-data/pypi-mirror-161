from multidict import MultiDict


def as_list(key, data):
    v = data.get(key)
    if isinstance(v, str):
        v = [v]
    elif not isinstance(v, list):
        v = []
    data[key] = v
    return data


def as_dict(data, key="data"):
    return {key: data} if not isinstance(data, dict) else data


def as_params(*, params=None, **kwargs):
    params = MultiDict(params if params is not None else {})
    params.update(kwargs)
    return params
