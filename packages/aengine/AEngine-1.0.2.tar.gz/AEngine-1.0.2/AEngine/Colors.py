class ColorMap:
    def __init__(self, color_map_dict):
        for k, v in color_map_dict.items():
            self.__dict__[k] = v

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __getitem__(self, item):
        return self.__dict__["item"]


class Color:
    def __init__(self, *args, **kwargs):
        if len(args) == 1 and len(args[0]) == 3:
            self.r = args[0][0]
            self.g = args[0][1]
            self.b = args[0][2]

        elif len(args) == 3:
            self.r = args[0]
            self.g = args[1]
            self.b = args[2]

        elif len(args) == 0 and len(list(kwargs)) == 3:
            self.r = kwargs['r']
            self.g = kwargs['g']
            self.b = kwargs['b']

    def __str__(self):
        return f'rgb({self.r},{self.g},{self.b})'

    def __repr__(self):
        return f'Color({self.r}, {self.g}, {self.b})'


class ColorNames:
    red = Color(255, 0, 0)
    green = Color(0, 255, 0)
    blue = Color(0, 0, 255)
    yellow = Color(255, 255, 0)
    purple = Color(255, 0, 255)
    cyan = Color(0, 255, 255)
    grey = gray = Color(60, 60, 60)
    darkgrey = darkgray = Color(20, 20, 20)
    lightgrey = lightgray = Color(150, 150, 150)
    lightskyblue = Color(135, 206, 250)
    orange = Color(255, 150, 0)
