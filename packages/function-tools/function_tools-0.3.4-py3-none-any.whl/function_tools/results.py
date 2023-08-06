from typing import (
    List,
    Union,
)

from function_tools.errors import (
    BaseError,
)


class BaseRunnableResult:
    """
    Базовый класс результатов выполнения запускаемых объектов
    """

    def __init__(self, *args, **kwargs):
        # Ключ результата, используемый для идентификации результата
        self._key = ''
        self._message = ''

        self._entities: List[Union[BaseError, 'BaseRunnableResult']] = []

    @property
    def entities(self) -> List[Union[BaseError, 'BaseRunnableResult']]:
        """
        Возвращает все сущности результата
        """
        return self._entities

    @property
    def errors(self) -> List[BaseError]:
        """
        Возвращает ошибки из результата. Т.к. в качестве сущностей могут
        выступать как ошибки, так и результаты выполнения запускаемых объектов,
        предусмотрен рекурсивный поиск ошибок.
        """
        errors_list = []

        for entity in self._entities:
            if isinstance(entity, BaseError):
                errors_list.append(entity)
            elif isinstance(entity, BaseRunnableResult):
                errors_list.extend(entity.errors)

        return errors_list

    @property
    def has_errors(self) -> bool:
        """
        Показывает, если ли в результате ошибки
        """
        return bool(self.errors)

    @property
    def has_not_errors(self) -> bool:
        """
        Показывает, нет ли в результате ошибок
        """
        return not bool(self.errors)

    @property
    def key(self):
        return self._key

    @key.setter
    def key(self, key):
        self._key = key

    @property
    def message(self):
        return self._message

    @message.setter
    def message(self, message_):
        self._message = message_

    def append_entity(self, entity: Union[BaseError, 'BaseRunnableResult']):
        """
        Добавление сущности в результат
        """
        if entity not in self._entities:
            self._entities.append(entity)
