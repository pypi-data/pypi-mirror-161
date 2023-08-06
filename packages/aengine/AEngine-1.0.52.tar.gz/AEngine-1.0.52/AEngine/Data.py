class Obj(dict):
    __default = None

    def __init__(self, *args, **kwargs):
        if len(args) > 0:
            if isinstance(args[0], dict):
                for k, v in args[0].items():
                    self.__dict__[k] = v
        for k, v in kwargs.items():
            self.__dict__[k] = v

        super().__init__(self.__dict__)

    def __str__(self):
        s = ""
        dct = self.__dict__.copy()
        if "_Obj__default" in list(dct):
            del dct["_Obj__default"]
        for i in list(dct):
            s += f"{i} => {dct[i]}, "
        s = s[:-2]
        return f"AEngine.Obj({s})"

    def __getitem__(self, item):
        try:
            return super().__getitem__(item)
        except KeyError:
            return self.default

    def __getattr__(self, item):
        try:
            return self.__dict__["item"]
        except KeyError:
            return self.default

    def extend(self, _dict: dict):
        for k, v in _dict.items():
            super().__setitem__(k, v)
            self.__setattr__(k, v)
        self.update()

    @property
    def default(self):
        return self.__default

    @default.setter
    def default(self, value):
        self.__default = value

    def get(self, value):
        return self.__getitem__(value)


class Chain:
    def __init__(self, llist=None):
        if llist is None:
            llist = []
        self.__list = llist

        for i in range(len(self.__list) - 1):
            self.__dict__[self.__list[i]] = self.__list[i + 1]

        self.__dict__[self.__list[-1]] = self.__list[0]

    def __str__(self):
        s = ""
        dct = self.__dict__.copy()
        del dct["_Chain__list"]
        for i in list(dct):
            s += f"{i} => {dct[i]}, "
        s = s[:-2]
        return f"AEngine.Chain({s})"

    def __repr__(self):
        return self.__str__()

    def __getitem__(self, item):
        return self.__dict__[item]

    def __update(self):
        for i in range(len(self.__list) - 1):
            self.__dict__[self.__list[i]] = self.__list[i + 1]

        self.__dict__[self.__list[-1]] = self.__list[0]

    def pop(self, index):
        del self.__dict__[index]
        self.__list.pop(self.__list.index(index))
        self.__update()

    def index(self, value):
        return self.__list[self.__list.index(value) - 1]
