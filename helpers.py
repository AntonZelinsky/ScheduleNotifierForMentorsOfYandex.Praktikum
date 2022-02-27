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


def str_to_time(str_time):
    return datetime.datetime.strptime(str_time, '%H:%M').time()


def plural(count: int, forms: list) -> str:
    """
    Возвращает строку со склоненным словом
    :param count: число для склонения
    :param forms: формы слова. [день, дня, дней]
    :return:
    """
    if count % 100 in (11, 12, 13, 14):
        return forms[2]
    if count % 10 == 1:
        return forms[0]
    if count % 10 in (2, 3, 4):
        return forms[1]
    return forms[2]
