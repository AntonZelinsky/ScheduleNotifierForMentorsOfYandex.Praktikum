import datetime


class Objectify:
    def __init__(self, in_dict: dict):
        assert isinstance(in_dict, dict)
        for key, val in in_dict.items():
            if isinstance(val, (list, tuple)):
                setattr(self, key, [Objectify(x) if isinstance(x, dict) else x for x in val])
            else:
                setattr(self, key, Objectify(val) if isinstance(val, dict) else val)


class Expando(object):
    def __getattr__(self, attrname):
        return None


def strptime(str_time):
    return datetime.datetime.strptime(str_time, '%H:%M').time()
