from typing import (
    List,
)


class BaseError:
    """
    Базовый класс для создания возникающих ошибок для дальнейшей обработки и
    вывода
    """

    def __init__(
        self,
        message: str = '',
    ):
        self._message = message

    def as_list(self) -> List[str]:
        return [self._message]

    def as_str(self) -> str:
        return self._message
