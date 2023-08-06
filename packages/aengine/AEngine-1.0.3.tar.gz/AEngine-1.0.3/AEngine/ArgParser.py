import sys
from functools import lru_cache


class ArgumentList:
    """Singleton argument list"""
    __instance: object or list = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __setattr__(self, key, value):
        self.__dict__[key] = value

    def __setitem__(self, key, value):
        self.__setattr__(key, value)

    def __getitem__(self, item):
        return self.__dict__[item]

    def __repr__(self):
        endl = '\n    '
        s = f'ArgumentList({endl}'
        for i in self.__dict__:
            s += f'{i}: {self[i]}{endl}'
        s += '\r)'
        return s

    def __str__(self):
        return self.__repr__()

    def __getattr__(self, item):
        if item in list(self.__dict__):
            return self.__dict__[item]
        return False

    def items(self):
        return self.__dict__.items()

    def keys(self):
        return self.__dict__.keys()

    def values(self):
        return self.__dict__.values()


class ArgumentParser:
    args = ArgumentList()
    rules = {}
    without_values = []

    def __new__(cls, *opt, **options):
        if options and len(list(options)) > 0:
            cls.add_rule_dict(options.get('rules'))
        elif opt and len(opt) > 0 and isinstance(opt, dict):
            cls.add_rule_dict(opt[0])

    @classmethod
    @lru_cache()
    def parse(cls, args_list=None, prefix="-") -> ArgumentList:
        _keys: list = []
        _values: list = []
        if args_list is None:
            args_list = sys.argv
        args_list.pop(0)
        for i in args_list:
            if i.startswith(prefix):
                _keys.append(i)
            else:
                _values.append(i)

        for i in range(len(_keys)):
            if _keys[i] in cls.without_values:
                _values.insert(i, True)
        _arg_dict: dict = dict(zip(_keys, _values))

        for i in list(_arg_dict):
            for rule in list(cls.rules):
                if i == cls.rules[rule] or (i in cls.rules[rule] and isinstance(cls.rules[rule], list)):
                    cls.args[rule] = _arg_dict[i]
                    break
            else:
                cls.args[i.strip(prefix).strip()] = _arg_dict[i]
        return cls.args

    @classmethod
    def add_rule(cls, _var_name: str | None = None, _flag: any = None):
        cls.rules[_var_name] = _flag

    @classmethod
    def add_rule_dict(cls, rules: dict):
        for k, v in rules.items():
            cls.add_rule(k, v)


if __name__ == '__main__':
    ArgumentParser.parse()
    print(ArgumentList())
