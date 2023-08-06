from dataclasses import dataclass


@dataclass
class Object(dict):
    __default = None

    def __init__(self, *args, **kwargs):
        if len(args) > 0:
            if isinstance(args[0], dict):
                for k, v in args[0].items():
                    self.__dict__[k] = v
        for k, v in kwargs.items():
            self.__dict__[k] = v

        super().__init__(self.__dict__)

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


obj = Object({"t": 12}, a=10, b=15)
obj.default = "kko"
obj.extend({"e": 10})

