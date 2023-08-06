from rich import print
from datetime import datetime


class Debug:
    @staticmethod
    def log(message, prefix=None, color='rgb(0,255,0)'):
        color = str(color)
        if prefix is None:
            prefix = '[Debug]'
        print(f'[{color} bold]{prefix}: {message}    --    {datetime.today().strftime("%H:%M:%S")}[/{color} bold]')
