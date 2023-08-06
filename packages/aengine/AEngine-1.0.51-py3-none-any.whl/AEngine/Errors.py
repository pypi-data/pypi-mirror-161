from datetime import datetime

from rich import print

from AEngine.Colors import ColorNames


class Error:
    status_code = -1

    @classmethod
    def raise_error(cls, message='', color=ColorNames.red):
        """raise error and exit with status code"""
        color = str(color)
        message = f'| {cls.__name__}: {message} | CODE: {cls.status_code}  | {datetime.today().strftime("%H:%M:%S")} |'
        separator = f'* {"-" * (len(message) - 4)} *'
        print(
            f'[{color}]'
            f'\n{separator}\n'
            f'{message}'
            f'\n{separator}\n'
            f'[/{color}]')
        raise RuntimeError

    @classmethod
    def raise_safely(cls, message='', color=ColorNames.red):
        """raise error without exit"""

        try:
            cls.raise_error(message, color)

        except RuntimeError as e:
            pass
