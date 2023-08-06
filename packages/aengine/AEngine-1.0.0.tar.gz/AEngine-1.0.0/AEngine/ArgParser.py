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

    def items(self):
        return self.__dict__.items()

    def keys(self):
        return self.__dict__.keys()

    def values(self):
        return self.__dict__.values()


class ArgumentParser:
    args = ArgumentList()
    rules = {}

    def __init__(self, **options):
        self.options = options
        _rulesLoaded = self.options.get('rules')
        if _rulesLoaded:
            self.rules = self.options.get('rules')

    @classmethod
    @lru_cache()
    def parse(cls, args_list=None) -> ArgumentList:
        """Parse command line args"""
        if args_list is None:
            args_list = sys.argv
        _arg_list = args_list
        _keys: list = _arg_list[1::2]
        _values: list = _arg_list[2::2]
        _arg_dict: dict = dict(zip(_keys, _values))

        for i in list(_arg_dict):
            for rule in list(cls.rules):
                if i == cls.rules[rule] or (i in cls.rules[rule] and isinstance(cls.rules[rule], list)):
                    cls.args[rule] = _arg_dict[i]
                    break
            else:
                cls.args[i.strip('-').strip()] = _arg_dict[i]
        return cls.args

    @classmethod
    def add_rule(cls, var_name: str | None, flag: any):
        """add rule for parsing\n.\n
        var_name - name of variable to save value.\n
        flag - flag, that starts with '-'
        """
        cls.rules[var_name] = flag

    @classmethod
    def add_rules_dict(cls, rules: dict):
        """"""
        for k, v in rules.items():
            cls.add_rule(v, k)


if __name__ == '__main__':
    ArgumentParser.parse()
    print(ArgumentList())

