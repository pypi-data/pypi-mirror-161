from peb import isiter


def raise_or(e, value, throw=False):
    if throw:
        raise e
    return value


def safeaccess(obj, s, default=None):
    if not obj or not s:
        return default
    value = obj
    args = s.split('.')

    try:
        for arg in args:
            if type(value) is dict:
                value = value[arg]
            elif isiter(value, allow_dict=False):
                value = value[int(arg)]
            else:
                return default
    except (IndexError, KeyError, ValueError):
        return default

    return value
