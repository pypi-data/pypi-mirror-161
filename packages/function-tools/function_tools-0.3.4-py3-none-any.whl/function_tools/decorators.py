from functools import (
    wraps,
)


def run_without_errors(func):
    """
    Декоратор методов функции запускаемых только в случае отсутствия зарегистрированных ошибок в процессе работы
    """

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if self.result.has_not_errors:
            return func(self, *args, **kwargs)

    return wrapper
