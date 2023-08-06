from datetime import datetime

from rich import print

from AEngine.Colors import ColorNames


class Warn:
    @classmethod
    def raise_warning(cls, message, color=ColorNames.yellow):
        color = str(color)
        message = f'| {message} | Warning | {datetime.today().strftime("%H:%M:%S")} |'
        separator = f'* {"-" * (len(message) - 4)} *'
        print(
            f'[{color}]'
            f'\n{separator}\n'
            f'{message}'
            f'\n{separator}'
            f'[/{color}]'
        )
