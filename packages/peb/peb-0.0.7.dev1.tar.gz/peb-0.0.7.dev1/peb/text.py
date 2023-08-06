import base64
import json
import re

snake_first = re.compile('(.)([A-Z][a-z]+)')
snake_second = re.compile('([a-z0-9])([A-Z])')


def snake_to_camel(s):
    components = s.split('_')
    return ''.join(x.title() for x in components)


def camel_to_snake(s):
    s1 = re.sub(snake_first, r'\1_\2', s)
    return re.sub(snake_second, r'\1_\2', s1).lower()


def truncate(text, limit, suffix='...'):
    if text is None:
        return None
    return (text[:limit] + suffix) if len(text) > limit else text


def json_to_base64(data):
    s = json.dumps(data)
    b_encoded = base64.b64encode(s.encode())
    return b_encoded.decode()


def base64_to_json(s):
    b_decoded = base64.b64decode(s)
    return json.loads(b_decoded)
